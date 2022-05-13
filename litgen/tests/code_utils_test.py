import os, sys;

import pytest

THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
from code_types import *
from options import CodeStyleOptions
import code_utils


def test_strip_empty_lines():
    code_lines = """
    
          struct Foo {
             int a = 1;
          };
    """.split('\n')
    code_lines = code_utils.strip_empty_lines(code_lines)
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


    with pytest.raises(CppParseException):
        code_utils.parse_c_identifier_at_end("")

    with pytest.raises(CppParseException):
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
