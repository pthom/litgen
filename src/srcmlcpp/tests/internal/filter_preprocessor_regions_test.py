from __future__ import annotations
import os
import sys

from codemanip import code_utils

from srcmlcpp.internal import filter_preprocessor_regions, code_to_srcml

_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_preprocessor_test_state_and_inclusion_guards():
    header_acceptable_ifndef__regex = "_H$|ACCEPTED$"
    code = filter_preprocessor_regions._EXAMPLE_HEADER_FILE
    xml_header = code_to_srcml.code_to_srcml(code)
    xml_header_filtered = filter_preprocessor_regions.filter_preprocessor_regions(
        xml_header, header_acceptable_ifndef__regex
    )
    header_filtered = code_to_srcml.srcml_to_code(xml_header_filtered)
    code_utils.assert_are_codes_equal(header_filtered, filter_preprocessor_regions._EXPECTED_FILTERED_HEADER)


def _filter(code: str, header_acceptable__regex: str) -> str:
    xml_header = code_to_srcml.code_to_srcml(code)
    xml_header_filtered = filter_preprocessor_regions.filter_preprocessor_regions(xml_header, header_acceptable__regex)
    return code_to_srcml.srcml_to_code(xml_header_filtered)


def test_if_expression_macro_name_is_matched_against_regex():
    # `#if MY_MACRO` (and `#if defined(MY_MACRO)`) must participate in the same
    # name-based accept/reject as `#ifdef MY_MACRO`: the macro name is extracted from
    # the condition expression and matched against header_acceptable__regex.
    code = """
#if MY_MACRO
void FooIf();
#endif

#if defined(MY_MACRO)
void FooDefined();
#endif

#if OTHER_MACRO
void FooOther();
#endif
"""

    # When MY_MACRO is acceptable, both MY_MACRO-guarded regions are kept,
    # while the OTHER_MACRO region is dropped.
    expected = """
#if MY_MACRO
void FooIf();
#endif

#if defined(MY_MACRO)
void FooDefined();
#endif
"""
    code_utils.assert_are_codes_equal(_filter(code, "MY_MACRO"), expected)

    # When no macro is acceptable, every #if region is dropped.
    code_utils.assert_are_codes_equal(_filter(code, "__cplusplus"), "")


def test_extract_macro_name_from_if_expr():
    cases = {
        "#if MY_MACRO": "MY_MACRO",
        "#if defined(MY_MACRO)": "MY_MACRO",
        "#if MY_MACRO > 5": "MY_MACRO",
        "#if !defined(MY_MACRO)": "MY_MACRO",
        # compound conditions are best-effort: the first referenced name is returned
        "#if defined(A) && !defined(B)": "A",
    }
    for code, expected in cases.items():
        directive = list(code_to_srcml.code_to_srcml(code))[0]
        got = filter_preprocessor_regions._extract_macro_name_from_if_expr(directive)
        assert got == expected, f"{code!r}: got {got!r}, expected {expected!r}"
