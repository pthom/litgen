from __future__ import annotations
import os
import sys

from codemanip import code_utils


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_line_python_comment_position():
    """
    Note: parsing comment position in python is complex.
    This method applies naive strategies. May be use the python official parser module?
    Example comments that it can handle:
        a = 5 # my comment
        a = 5 # my "comment"
        a = 5 # my "comment" with # inside
        a = "#" # my comment
        a = '#' # my comment
        a = '''#''' # my comment
    """
    code = "a = 5 # my comment"
    assert code_utils.line_python_comment_position(code) == 6

    code = 'a = 5 # my "comment"'
    assert code_utils.line_python_comment_position(code) == 6

    code = 'a = 5 # my "comment" with # inside'
    assert code_utils.line_python_comment_position(code) == 6

    code = 'a = "#" # my comment'
    assert code_utils.line_python_comment_position(code) == 8

    code = "a = '#' # my comment"
    assert code_utils.line_python_comment_position(code) == 8

    code = "a = '''#''' # my comment"
    assert code_utils.line_python_comment_position(code) == 12

    code = "        # my comment"
    assert code_utils.line_python_comment_eol_position(code) is None


def test_align_python_comments_in_block():
    code = """
a = 5 # c
aa = 5 # c
# cc
    """
    expected = """
a = 5  # c
aa = 5 # c
# cc
    """
    generated = code_utils.align_python_comments_in_block(code)
    assert generated == expected


def test_strip_empty_lines():
    code_lines = """

          struct Foo {
             int a = 1;
          };
    """.split(
        "\n"
    )
    code_lines = code_utils.strip_empty_lines_in_list(code_lines)  # type: ignore
    code_stripped = "\n".join(code_lines)
    assert (
        code_stripped
        == """          struct Foo {
             int a = 1;
          };"""
    )


def test_to_snake_case():
    assert code_utils.to_snake_case("VSliderFloat") == "v_slider_float"
    assert code_utils.to_snake_case("CamelCase") == "camel_case"
    assert code_utils.to_snake_case("ToRGB") == "to_rgb"
    assert code_utils.to_snake_case("CvMat_To_Array") == "cv_mat_to_array"
    assert code_utils.to_snake_case("__repr__") == "__repr__"
    assert code_utils.to_snake_case("ConfigMacOSXBehaviors") == "config_mac_osx_behaviors"
    assert code_utils.to_snake_case("SizeOfIDStack") == "size_of_id_stack"
    # assert code_utils.to_snake_case("RGBtoHSV") == "rgb_to_hsv"  (from imgui.h : this one is too tricky)


def test_unindent_code():
    code = """
    a = 5
    if a > 10:
        return 0
    """
    assert (
        code_utils.unindent_code(code)
        == """
a = 5
if a > 10:
    return 0
"""
    )


def test_var_name_contains_word():
    assert code_utils.var_name_contains_word("item_count", "count")
    assert code_utils.var_name_contains_word("count", "count")
    assert code_utils.var_name_contains_word("count_items", "count")
    assert not code_utils.var_name_contains_word("countitems", "count")

    assert code_utils.var_name_contains_word("itemCount", "Count")
    assert code_utils.var_name_contains_word("countItems", "Count")
    assert code_utils.var_name_contains_word("count_Items", "Count")


def test_contains_word():
    assert code_utils.contains_word("Hello wonderful world", "wonderful")
    assert not code_utils.contains_word("Hello wonderful world", "Wonderful")
    assert code_utils.contains_word("Hello wonderful world", "Hello")
    assert code_utils.contains_word("Hello wonderful world", "world")
    assert not code_utils.contains_word("Hello wonderful world", "worl")
    assert not code_utils.contains_word("Hello wonderful world", "Hell")
    assert not code_utils.contains_word("const int8_t*", "T*")


def test_contains_pointer_type():
    assert code_utils.contains_pointer_type("const int8_t*", "int8_t*")
    assert code_utils.contains_pointer_type("int8_t*", "int8_t*")
    assert not code_utils.contains_pointer_type("const int8_t*", "T*")

    assert not code_utils.contains_pointer_type("uint8_t*", "int8_t*")
    assert not code_utils.contains_pointer_type("int8_t*", "uint8_t*")


def test_assert_are_code_equal():
    expected = """
    a
        b
        c

    """
    generated = """
a
    b
    c
"""
    code_utils.assert_are_codes_equal(generated, expected)


#     expected = """
# Hello,
# World!
#     """
#
#     generated = """
# Hello,
# Big World!
#     """
#     code_utils.assert_are_codes_equal(generated, expected)


def test_line_comment_position():
    line = "int a;"
    assert code_utils.line_cpp_comment_position(line) is None

    line = "int a; // Test"
    assert code_utils.line_cpp_comment_position(line) == 7

    line = 'std::string r="// Tricky \\" string" // Final comment'
    assert code_utils.line_cpp_comment_position(line) == 36

    line = 'std::string s="// Super " Tricky string"'
    assert code_utils.line_cpp_comment_position(line) is None


def test_last_code_position_before_comment():
    line = "int a;"
    assert code_utils.last_code_position_before_cpp_comment(line) == 6

    line = "int a; // Test"
    assert code_utils.last_code_position_before_cpp_comment(line) == 6

    line = 'std::string r="// Tricky \\" string" // Final comment'
    assert code_utils.last_code_position_before_cpp_comment(line) == 35

    line = ""
    assert code_utils.last_code_position_before_cpp_comment(line) == 0


def test_join_lines_with_token_before_comment():
    lines = [
        "int a = 0",
        "int b = 1 // Dummy comment",
        'std::string r="// Tricky string" // Final comment',
        'std::string s="// Tricky string"',
    ]

    r = code_utils.join_lines_with_token_before_cpp_comment(lines, ",")
    code_utils.assert_are_codes_equal(
        r,
        """
        int a = 0,
        int b = 1, // Dummy comment
        std::string r="// Tricky string", // Final comment
        std::string s="// Tricky string"
    """,
    )


def test_find_word_after_token():
    code = "return_value_policy::reference"
    r = code_utils.find_word_after_token(code, "return_value_policy::")
    assert r == "reference"

    code = "return_value_policy::reference // Yes"
    r = code_utils.find_word_after_token(code, "return_value_policy::")
    assert r == "reference"
