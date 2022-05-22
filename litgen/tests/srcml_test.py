import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import litgen.internal.srcml as srcml
import litgen.internal.code_utils as code_utils


def assert_code_unmodified_by_srcml(code: str):
    """
    We transform the code to xml (srcML), and assert that it can safely be translated back to the same code
    """
    root = srcml.code_to_srcml(code)
    code2 = srcml.srcml_to_code(root)
    assert code2 == code


def test_srcml_does_not_modify_code():
    assert_code_unmodified_by_srcml("int a = 1;")
    assert_code_unmodified_by_srcml("void foo(int x, int y=5){};")
    assert_code_unmodified_by_srcml("""
    #include <nonexistingfile.h>
    #define TRUC
    // A super nice function
    template<typename T> constexpr T add(const T& a, T b) { return a + b;}
    
    /* A dummy comment */
                            ;;TRUC;;TRUC; TRUC TRUC   ;;;; // and some gratuitous elements
    // A lambda
    auto fnSub = [](int a, int b) { return b - a;};
    """)


def test_parse_cpp_decl_statement():
    code = "int a = 1;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    print(cpp_decl_statement)



test_parse_cpp_decl_statement()