from __future__ import annotations
import copy
from typing import Optional
from xml.etree import ElementTree as ET

from codemanip import code_utils

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

_EXPECTED_FILTERED_HEADER = """
#ifndef MY_HEADER_H   // We are in the main header, and this comment should be included (the previous ifndef was just an inclusion guard)

void Foo() {}     // This function and this comment should be included

#ifdef SOME_OPTION_ACCEPTED
// We are entering a zone which we want to accept if we add "ACCEPTED$" to options.header_acceptable__regex
void FooAccepted();
#endif

#endif
"""


class _SrcmlPreprocessorState:
    """We ignore everything that is inside a #ifdef/#if/#ifndef  region
    but we try to keep what is inside the header inclusion guard ifndef region.

    We will test that a ifndef is an inclusion guard by checking comparing its suffix with HEADER_GUARD_SUFFIXES
    """

    header_acceptable__regex: str

    was_last_element_an_ignored_endif: bool = False
    last_ignored_preprocessor_stmt_line: int = -1
    last_element: Optional[ET.Element] = None

    encountered_if: list[str]
    debug = False

    def __init__(self, header_acceptable__regex: str) -> None:
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

    def process_tag(self, element: ET.Element) -> None:
        self.last_element = element
        tag = srcml_utils.clean_tag_or_attrib(element.tag)

        is_ifdef = tag in ["ifdef", "if", "endif", "else", "elif", "ifndef"]

        end = srcml_utils.element_end_position(element)
        if end is None:
            return
        element_line = end.line

        def extract_ifdef_var_name() -> str:
            if not is_ifdef:
                return ""
            for child in element:
                if srcml_utils.clean_tag_or_attrib(child.tag) == "name":
                    assert child.text is not None
                    return child.text
            return ""

        ifdef_var_name = extract_ifdef_var_name()

        self.was_last_element_an_ignored_endif = False
        if tag in ["ifdef", "if"]:
            self.last_ignored_preprocessor_stmt_line = element_line
            self.encountered_if.append(ifdef_var_name)
        elif tag == "ifndef":
            self.last_ignored_preprocessor_stmt_line = element_line
            self.encountered_if.append(ifdef_var_name)
        elif tag == "endif":
            if self.has_one_excluded_ifdef():
                self.was_last_element_an_ignored_endif = True
            self.last_ignored_preprocessor_stmt_line = element_line
            # Note: with extern "C" blocks, we might encounter the #ifdef / #endif out of order
            # so that we cannot rely on having len(self.encountered_if) > 0
            # assert len(self.encountered_if) > 0
            if len(self.encountered_if) > 0:
                self.encountered_if = self.encountered_if[:-1]
        elif tag in ["else", "elif"]:
            self.last_ignored_preprocessor_stmt_line = element_line

        if self.debug and is_ifdef:
            self._log_state(element)

    def has_one_excluded_ifdef(self) -> bool:
        for ifdef_var_name in self.encountered_if:
            if not code_utils.does_match_regex(self.header_acceptable__regex, ifdef_var_name):
                return True
        return False

    def shall_ignore(self) -> bool:
        if self.was_last_element_an_ignored_endif:
            return True
        if self.last_element is None:
            return False
        if srcml_utils.clean_tag_or_attrib(self.last_element.tag) == "comment":
            start = srcml_utils.element_start_position(self.last_element)
            if start is not None:
                comment_line = start.line
                if comment_line == self.last_ignored_preprocessor_stmt_line:
                    return True

        r = self.has_one_excluded_ifdef()
        return r


def filter_preprocessor_regions(unit: ET.Element, header_acceptable__regex: str) -> ET.Element:
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
