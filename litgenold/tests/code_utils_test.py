import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
from typing import Tuple
import pytest

import litgen
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


def test_parse_c_identifier_at_start() -> Tuple[str, int]:
    id, pos = code_utils.parse_c_identifier_at_start("a")
    assert id == "a"
    assert pos == 1

    id, pos = code_utils.parse_c_identifier_at_start("_abcd_000* int")
    assert id == "_abcd_000"
    assert pos == 9

    with pytest.raises(ValueError):
        code_utils.parse_c_identifier_at_start("")

    with pytest.raises(ValueError):
        code_utils.parse_c_identifier_at_start("float value")


def test_parse_c_identifier_at_end() -> Tuple[str, int]:
    id, pos = code_utils.parse_c_identifier_at_end("a")
    assert id == "a"
    assert pos == 0

    id, pos = code_utils.parse_c_identifier_at_end("int*abc")
    assert id == "abc"
    assert pos == 4

    id, pos = code_utils.parse_c_identifier_at_end("int*0abc")
    assert id == ""
    assert pos == -1


    with pytest.raises(litgen.CppParseException):
        code_utils.parse_c_identifier_at_end("")

    with pytest.raises(litgen.CppParseException):
        code_utils.parse_c_identifier_at_end("value float")


def test_parse_function_declaration():
    code_line = "void foo() {}"
    r = code_utils.parse_function_declaration(code_line)
    assert r.return_type_cpp == "void"
    assert r.name_cpp == "foo"

    code_line = "std::function<int(void)> function;"
    assert code_utils.parse_function_declaration(code_line) is None

    # cf https://en.wikipedia.org/wiki/Most_vexing_parse
    code_line= "TimeKeeper time_keeper(Timer());"         # This is a function declaration, not a variable decl + init!
    r = code_utils.parse_function_declaration(code_line)
    assert r.name_cpp == "time_keeper"
    assert r.return_type_cpp == "TimeKeeper"

    code_line= "TimeKeeper time_keeper = Timer();"         # This is a variable decl + init!
    r = code_utils.parse_function_declaration(code_line)
    assert r is None

    code_line= "double  operator[] (size_t idx) const { return (&x)[idx]; }"
    r = code_utils.parse_function_declaration(code_line)
    assert r.name_cpp == "operator[]"
    assert r.return_type_cpp == "double"

    code_line= "    std::function<int(void)>  operator() (std::vector<int>& a) const { return (&x)[idx]; }"
    r = code_utils.parse_function_declaration(code_line)
    assert r.name_cpp == "operator()"
    assert r.return_type_cpp == "std::function<int(void)>"


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
