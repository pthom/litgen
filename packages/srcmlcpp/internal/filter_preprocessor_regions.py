import copy
from typing import List, Optional
from xml.etree import ElementTree as ET

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

#endif // #ifndef MY_HEADER_H
    """

_EXPECTED_FILTERED_HEADER = """
// We are in the main header, and this comment should be included (the previous ifndef was just an inclusion guard)

void Foo() {}     // This function and this comment should be included


"""


class _SrcmlPreprocessorState:
    """We ignore everything that is inside a #ifdef/#if/#ifndef  region
    but we try to keep what is inside the header inclusion guard ifndef region.

    We will test that a ifndef is an inclusion guard by checking comparing its suffix with HEADER_GUARD_SUFFIXES
    """

    header_acceptable_suffixes: List[str]

    was_last_element_a_preprocessor_stmt: bool = False
    last_preprocessor_stmt_line: int = -1
    last_element: Optional[ET.Element] = None

    count_preprocessor_tests = 0

    debug = False

    def __init__(self, header_acceptable_suffixes: List[str]) -> None:
        self.header_acceptable_suffixes = header_acceptable_suffixes

    def _log_state(self, element: ET.Element) -> str:
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

        info = f"Line: {line:04} {self.count_preprocessor_tests=} {element_code}"
        print(info)

    def process_tag(self, element: ET.Element) -> None:
        self.last_element = element
        tag = srcml_utils.clean_tag_or_attrib(element.tag)

        end = srcml_utils.element_end_position(element)
        if end is None:
            return
        element_line = end.line
        if element_line == 416:
            print("f")

        def extract_ifndef_name() -> str:
            for child in element:
                if srcml_utils.clean_tag_or_attrib(child.tag) == "name":
                    assert child.text is not None
                    return child.text
            return ""

        def is_inclusion_guard_ifndef() -> bool:
            ifndef_name = extract_ifndef_name()
            for suffix in self.header_acceptable_suffixes:
                if ifndef_name.upper().endswith(suffix.upper()):
                    return True
            return False

        self.was_last_element_a_preprocessor_stmt = False
        if tag in ["ifdef", "if"]:
            self.was_last_element_a_preprocessor_stmt = True
            self.last_preprocessor_stmt_line = element_line
            self.count_preprocessor_tests += 1
        elif tag == "endif":
            self.was_last_element_a_preprocessor_stmt = True
            self.last_preprocessor_stmt_line = element_line
            self.count_preprocessor_tests -= 1
        elif tag in ["else", "elif"]:
            self.was_last_element_a_preprocessor_stmt = True
            self.last_preprocessor_stmt_line = element_line
        elif tag == "ifndef":
            self.was_last_element_a_preprocessor_stmt = True
            self.last_preprocessor_stmt_line = element_line
            if not is_inclusion_guard_ifndef():
                self.count_preprocessor_tests += 1

        if tag in ["ifdef", "if", "endif", "else", "elif", "ifndef"]:
            self._log_state(element)

    def shall_ignore(self) -> bool:
        assert self.count_preprocessor_tests >= -1  # -1 because we can ignore the inclusion guard
        if self.was_last_element_a_preprocessor_stmt:
            return True
        if self.last_element is None:
            return False
        if srcml_utils.clean_tag_or_attrib(self.last_element.tag) == "comment":
            start = srcml_utils.element_start_position(self.last_element)
            if start is not None:
                comment_line = start.line
                if comment_line == self.last_preprocessor_stmt_line:
                    return True

        if self.count_preprocessor_tests > 0:
            return True
        else:
            return False


def filter_preprocessor_regions(unit: ET.Element, header_acceptable_suffixes: List[str]) -> ET.Element:
    filtered_unit = copy.deepcopy(unit)
    processor = _SrcmlPreprocessorState(header_acceptable_suffixes)
    children_to_remove = []

    for child in filtered_unit:
        processor.process_tag(child)
        if processor.shall_ignore():
            children_to_remove.append(child)

    for child_to_remove in children_to_remove:
        filtered_unit.remove(child_to_remove)

    return filtered_unit
