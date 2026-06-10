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


def test_else_branch_content_is_dropped():
    # The `#else` branch is inactive: only the primary `#ifdef` branch is kept when the
    # region is accepted. The `#else`/`#endif` markers themselves are preserved.
    code = """
#ifdef MY_MACRO
void Primary();
#else
void Secondary();
#endif
"""
    expected_accepted = """
#ifdef MY_MACRO
void Primary();
#else
#endif
"""
    code_utils.assert_are_codes_equal(_filter(code, "MY_MACRO"), expected_accepted)

    # When the region is rejected, both branches (and the markers) are dropped.
    code_utils.assert_are_codes_equal(_filter(code, "OTHER"), "")


def test_else_branch_of_accepted_ifndef_is_dropped():
    # Same behavior for `#ifndef` (e.g. an inclusion-guard-like region).
    code = """
#ifndef MY_GUARD
void Primary();
#else
void Secondary();
#endif
"""
    expected = """
#ifndef MY_GUARD
void Primary();
#else
#endif
"""
    code_utils.assert_are_codes_equal(_filter(code, "MY_GUARD"), expected)


def test_only_primary_branch_is_kept_in_if_elif_else_chain():
    # `#elif` branches are treated as inactive like `#else`: only the primary `#if`
    # branch is kept (best-effort; this is a name match, not a value evaluation).
    code = """
#if MACRO_A
void A();
#elif MACRO_B
void B();
#else
void C();
#endif
"""
    expected = """
#if MACRO_A
void A();
#elif MACRO_B
#else
#endif
"""
    code_utils.assert_are_codes_equal(_filter(code, "MACRO_A"), expected)


def test_else_inside_accepted_inclusion_guard_drops_nested_secondary_branch():
    # A nested `#ifdef ... #else ... #endif` inside the kept inclusion guard: the nested
    # `#else` content is dropped, the primary nested branch is kept.
    code = """
#ifndef MY_HEADER_H
void Always();
#ifdef MY_MACRO
void Primary();
#else
void Secondary();
#endif
#endif
"""
    expected = """
#ifndef MY_HEADER_H
void Always();
#ifdef MY_MACRO
void Primary();
#else
#endif
#endif
"""
    code_utils.assert_are_codes_equal(_filter(code, "_H$|MY_MACRO"), expected)


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
