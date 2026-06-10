from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree as ET

from codemanip import code_utils
from codemanip.code_utils import RegexOrMatcher

import srcmlcpp
from srcmlcpp.internal import srcml_utils

"""
Filters a code unit (i.e a file) a removes regions that are inside preprocessor tests
(except for header inclusion guards)

See examples below:
"""

_EXAMPLE_HEADER_FILE = """
#ifndef MY_HEADER_H   // This ifndef should be removed, as well as this comment
// We are in the main header, and this comment should be included (the previous ifndef was just an inclusion guard)

void Foo() {}     // This function and this comment should be included

#ifdef SOME_OPTION
// We are probably entering a zone that handle arcane options and should not be included in the bindings
void Foo2() {}    // this should be ignored
#else
void Foo3() {}    // this should be ignored also
#endif // #ifdef SOME_OPTION  <- this comment should be removed (on same line as an ifdef/endif)

#ifndef WIN32
// We are also probably entering a zone that handle arcane options and should not be included in the bindings
void Foo4() {}
#endif

#ifdef SOME_OPTION_ACCEPTED
// We are entering a zone which we want to accept if we add "ACCEPTED$" to options.header_acceptable__regex
void FooAccepted();
#endif

#endif // #ifndef MY_HEADER_H
    """


def _extract_macro_name_from_if_expr(element: ET.Element) -> str:
    """Extract the first macro name referenced in a `#if` condition.

    Unlike `#ifdef`/`#ifndef` (whose macro name is a direct `<name>` child of the
    directive), `#if` stores the condition inside an `<expr>` subtree. We walk
    that subtree in document order and return the first referenced macro name, so that
    `#if MY_MACRO` and `#if defined(MY_MACRO)` can be matched against
    `header_acceptable__regex` exactly like `#ifdef MY_MACRO`.

    This is intentionally *not* a C-expression evaluator: compound conditions such as
    `#if defined(A) && !defined(B)` are handled on a best-effort basis (the first name,
    here `A`, is returned). The `defined` operator itself is skipped so that its argument
    is used instead.
    """

    def visit(node: ET.Element) -> str:
        for child in node:
            tag = srcml_utils.clean_tag_or_attrib(child.tag)
            if tag == "name":
                if child.text is not None and child.text != "defined":
                    return child.text
            elif tag == "argument":
                # `defined(MY_MACRO)` stores the argument as plain text;
                # in compound expressions it nests an <expr> instead.
                if child.text is not None and child.text.strip() != "":
                    return child.text.strip()
            found = visit(child)
            if found != "":
                return found
        return ""

    return visit(element)


_EXPECTED_FILTERED_HEADER = """
#ifndef MY_HEADER_H   // We are in the main header, and this comment should be included (the previous ifndef was just an inclusion guard)

void Foo() {}     // This function and this comment should be included

#ifdef SOME_OPTION_ACCEPTED
// We are entering a zone which we want to accept if we add "ACCEPTED$" to options.header_acceptable__regex
void FooAccepted();
#endif

#endif
"""


@dataclass
class _CppConditionRegion:
    """One open `#if / #ifdef / #ifndef ... #endif` region encountered while filtering."""

    # True if the region's primary guard macro does not match header_acceptable__regex.
    # It governs whether the region's directive markers and its primary-branch content are
    # kept, and never changes once the region is opened.
    region_excluded: bool
    # True once we have passed a `#else` or `#elif`. The content of these secondary branches
    # is always dropped (issue #46: only the primary `#if` branch is treated as active),
    # even when the region itself is kept.
    in_secondary_branch: bool = False


class _SrcmlPreprocessorState:
    """We ignore everything that is inside a #ifdef/#if/#ifndef  region
    but we try to keep what is inside the header inclusion guard ifndef region.

    We will test that a ifndef is an inclusion guard by checking comparing its suffix with HEADER_GUARD_SUFFIXES

    `#else`/`#elif` branches are treated as inactive: their content is always dropped, so that an
    accepted `#ifdef MY_MACRO ... #else ... #endif` keeps only the primary branch (issue #46).
    """

    header_acceptable__regex: RegexOrMatcher

    was_last_element_an_ignored_endif: bool = False
    last_ignored_preprocessor_stmt_line: int = -1
    last_element: Optional[ET.Element] = None

    encountered_if: list[_CppConditionRegion]
    debug = False

    def __init__(self, header_acceptable__regex: RegexOrMatcher) -> None:
        self.header_acceptable__regex = header_acceptable__regex
        self.shall_exclude = False
        self.encountered_if = []

    def _log_state(self, element: ET.Element) -> None:
        if not self.debug:
            return

        options = srcmlcpp.SrcmlcppOptions()
        wrapper = srcmlcpp.SrcmlWrapper(options, element, None)

        element_code = wrapper.str_code_verbatim()
        while element_code.endswith("\n"):
            element_code = element_code[:-1]

        line = 0
        end = srcml_utils.element_end_position(element)
        if end is not None:
            line = end.line

        info = f"Line: {line:04} {element_code} => {self.encountered_if=}"
        print(info)

    def _macro_name(self, element: ET.Element, tag: str) -> str:
        # `#if` stores its condition inside an <expr> subtree, so the macro name is
        # not a direct <name> child (unlike `#ifdef`/`#ifndef`).
        if tag == "if":
            return _extract_macro_name_from_if_expr(element)
        for child in element:
            if srcml_utils.clean_tag_or_attrib(child.tag) == "name":
                assert child.text is not None
                return child.text
        return ""

    def _is_acceptable(self, macro_name: str) -> bool:
        return code_utils.does_match_regex_or_matcher(self.header_acceptable__regex, macro_name)

    def process_tag(self, element: ET.Element) -> None:
        self.last_element = element
        tag = srcml_utils.clean_tag_or_attrib(element.tag)

        is_directive = tag in ["ifdef", "if", "endif", "else", "elif", "ifndef"]

        end = srcml_utils.element_end_position(element)
        if end is None:
            return
        element_line = end.line

        self.was_last_element_an_ignored_endif = False
        if tag in ["ifdef", "if", "ifndef"]:
            macro_name = self._macro_name(element, tag)
            self.encountered_if.append(_CppConditionRegion(region_excluded=not self._is_acceptable(macro_name)))
            self.last_ignored_preprocessor_stmt_line = element_line
        elif tag in ["else", "elif"]:
            if len(self.encountered_if) > 0:
                self.encountered_if[-1].in_secondary_branch = True
            self.last_ignored_preprocessor_stmt_line = element_line
        elif tag == "endif":
            # Decide whether the #endif marker itself is dropped *before* popping its region.
            self.was_last_element_an_ignored_endif = self._directive_is_excluded()
            self.last_ignored_preprocessor_stmt_line = element_line
            # Note: with extern "C" blocks, we might encounter the #ifdef / #endif out of order
            # so that we cannot rely on having len(self.encountered_if) > 0
            # assert len(self.encountered_if) > 0
            if len(self.encountered_if) > 0:
                self.encountered_if = self.encountered_if[:-1]

        if self.debug and is_directive:
            self._log_state(element)

    def _content_is_excluded(self) -> bool:
        # Content (anything that is not a preprocessor directive) is dropped if any enclosing
        # region is excluded, or if we are in any enclosing region's secondary (#else/#elif) branch.
        return any(region.region_excluded or region.in_secondary_branch for region in self.encountered_if)

    def _directive_is_excluded(self) -> bool:
        # A directive marker (#ifdef/#else/#endif/...) is kept whenever its region is accepted,
        # even inside a dropped branch — so an accepted `#ifdef X ... #else ... #endif` still
        # renders its `# #else` / `# #endif` markers. It is dropped only when its own region is
        # excluded, or when an *enclosing* region drops its content.
        if len(self.encountered_if) == 0:
            return False
        innermost = self.encountered_if[-1]
        if innermost.region_excluded:
            return True
        return any(region.region_excluded or region.in_secondary_branch for region in self.encountered_if[:-1])

    def shall_ignore(self) -> bool:
        if self.last_element is None:
            return False
        tag = srcml_utils.clean_tag_or_attrib(self.last_element.tag)

        if tag == "comment":
            start = srcml_utils.element_start_position(self.last_element)
            if start is not None and start.line == self.last_ignored_preprocessor_stmt_line:
                # A comment trailing a preprocessor directive is stripped together with it.
                return True
            return self._content_is_excluded()

        if tag == "endif":
            # Computed before the region was popped (see process_tag).
            return self.was_last_element_an_ignored_endif
        if tag in ["ifdef", "if", "ifndef", "else", "elif"]:
            return self._directive_is_excluded()

        return self._content_is_excluded()


def filter_preprocessor_regions(unit: ET.Element, header_acceptable__regex: RegexOrMatcher) -> ET.Element:
    filtered_unit = copy.deepcopy(unit)
    processor = _SrcmlPreprocessorState(header_acceptable__regex)
    children_to_remove = []

    for child in filtered_unit:
        processor.process_tag(child)
        if processor.shall_ignore():
            children_to_remove.append(child)

    for child_to_remove in children_to_remove:
        filtered_unit.remove(child_to_remove)

    return filtered_unit
