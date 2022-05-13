import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
import find_functions_structs_enums
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot


def test_fill_pydef_body_code():
    # Simple test / struct
    code_lines = """
    struct Foo {
        int a = 1;
        bool v;}
    """.split("\n")
    pydef_code = PydefCode(CppCodeType.STRUCT)
    find_functions_structs_enums._fill_pydef_body_code(code_lines, CppCodeType.STRUCT, pydef_code)
    assert pydef_code.body_code_cpp == '{\n        int a = 1;\n        bool v;}'

    # Simple test / function
    code_lines = "void foo(int a; bool b = true)".split("\n")
    pydef_code = PydefCode(CppCodeType.FUNCTION)
    find_functions_structs_enums._fill_pydef_body_code(code_lines, CppCodeType.FUNCTION, pydef_code)
    assert pydef_code.body_code_cpp == '(int a; bool b = true)'

    # Test function with embedded "("
    code_lines = "void foo(int a; vector<int> v = vector<int>(10, 0))".split("\n")
    pydef_code = PydefCode(CppCodeType.FUNCTION)
    find_functions_structs_enums._fill_pydef_body_code(code_lines, CppCodeType.FUNCTION, pydef_code)
    assert pydef_code.body_code_cpp == '(int a; vector<int> v = vector<int>(10, 0))'

    # Test struct with embedded "{"
    code_lines = """
    struct Foo {
        struct { int g = 5 } gg;
        bool v;}
    """.split("\n")
    pydef_code = PydefCode(CppCodeType.STRUCT)
    find_functions_structs_enums._fill_pydef_body_code(code_lines, CppCodeType.STRUCT, pydef_code)
    assert pydef_code.body_code_cpp == '{\n        struct { int g = 5 } gg;\n        bool v;}'


def test_read_comment_on_top_of_line():
    code_lines = """
          // Title line 1
          // Title continued on line 2
          enum ImAxis_ {
    """.split('\n')
    options = code_style_implot()
    comment = find_functions_structs_enums._read_comment_on_top_of_line(code_lines, options, 3)
    assert comment == "Title line 1\nTitle continued on line 2"


def test_find_functions_struct_or_enums():
    code = """
// Enables an axis
IMPLOT_API void SetupAxis(ImAxis axis, const char* label = NULL, ImPlotAxisFlags flags = ImPlotAxisFlags_None);
// Sets the format of numeric axis labels. Formated values will be double
IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
    """
    options = code_style_implot()
    pydef_functions = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.FUNCTION, options)
    assert len(pydef_functions) == 2
    assert pydef_functions[0].name_cpp == "SetupAxis"
    assert pydef_functions[1].title_cpp == 'Sets the format of numeric axis labels. Formated values will be double'
    assert pydef_functions[1].title_python(options) == 'Sets the format of numeric axis labels. Formated values will be float'
