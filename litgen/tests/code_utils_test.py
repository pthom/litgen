import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")
import litgen.internal.code_utils as code_utils


def test_strip_empty_lines():
    code_lines = """
    
          struct Foo {
             int a = 1;
          };
    """.split('\n')
    code_lines = code_utils.strip_empty_lines_in_list(code_lines)
    code_stripped = "\n".join(code_lines)
    assert code_stripped == """          struct Foo {
             int a = 1;
          };"""


def test_to_snake_case():
    assert code_utils.to_snake_case("CamelCase") == "camel_case"
    assert code_utils.to_snake_case("ToRGB") == "to_rgb"
    assert code_utils.to_snake_case("CvMat_To_Array") == "cv_mat_to_array"


def test_unindent_code():
    code = """
    a = 5
    if a > 10:
        return 0
    """
    assert code_utils.unindent_code(code) == """
a = 5
if a > 10:
    return 0
"""


def test_contains_word():
    assert code_utils.contains_word("Hello wonderful world", "wonderful")
    assert not code_utils.contains_word("Hello wonderful world", "Wonderful")
    assert code_utils.contains_word("Hello wonderful world", "Hello")
    assert code_utils.contains_word("Hello wonderful world", "world")
    assert not code_utils.contains_word("Hello wonderful world", "worl")
    assert not code_utils.contains_word("Hello wonderful world", "Hell")
    assert not code_utils.contains_word('const int8_t*', 'T*')


def test_contains_pointer_type():
    assert code_utils.contains_pointer_type('const int8_t*', 'int8_t*')
    assert code_utils.contains_pointer_type('int8_t*', 'int8_t*')
    assert not code_utils.contains_pointer_type('const int8_t*', 'T*')

    assert not code_utils.contains_pointer_type('uint8_t*', 'int8_t*')
    assert not code_utils.contains_pointer_type('int8_t*', 'uint8_t*')


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
    assert code_utils.line_comment_position(line) is None

    line = "int a; // Test"
    assert code_utils.line_comment_position(line) == 7

    line = 'std::string r="// Tricky \\" string" // Final comment'
    assert code_utils.line_comment_position(line) == 36

    line = 'std::string s="// Super \" Tricky string"'
    assert code_utils.line_comment_position(line) is None


def test_last_code_position_before_comment():
    line = "int a;"
    assert code_utils.last_code_position_before_comment(line) == 6

    line = "int a; // Test"
    assert code_utils.last_code_position_before_comment(line) == 6

    line = 'std::string r="// Tricky \\" string" // Final comment'
    assert code_utils.last_code_position_before_comment(line) == 35

    line = ""
    assert code_utils.last_code_position_before_comment(line) == 0


def test_join_lines_with_token_before_comment():
    lines = [
        "int a = 0",
        "int b = 1 // Dummy comment",
        'std::string r="// Tricky string" // Final comment',
        'std::string s="// Tricky string"'
    ]

    r = code_utils.join_lines_with_token_before_comment(lines, ",")
    code_utils.assert_are_codes_equal(r, """
        int a = 0,
        int b = 1, // Dummy comment
        std::string r="// Tricky string", // Final comment
        std::string s="// Tricky string"
    """)
