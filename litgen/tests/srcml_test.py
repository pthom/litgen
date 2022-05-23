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


def test_srcml_xml():
    code = "int a = 1"
    element = srcml.code_to_srcml(code)
    xml_str = srcml.srcml_to_str(element)
    expected_xml_str = """<?xml version="1.0" ?>
        <ns0:unit xmlns:ns0="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++" filename="/var/folders/hj/vlpl655s0gz58f0tfgghv0g40000gn/T/tmph4tcp71f.h">
           <ns0:decl>
              <ns0:type>
                 <ns0:name>int</ns0:name>
              </ns0:type>
               
              <ns0:name>a</ns0:name>
               
              <ns0:init>
                 = 
                 <ns0:expr>
                    <ns0:literal type="number">1</ns0:literal>
                 </ns0:expr>
              </ns0:init>
           </ns0:decl>
        </ns0:unit>    
    """

    def remove_first_two_lines(s: str):
        # We remove the first lines because of the unwanted file name
        lines = s.splitlines()
        r = "\n".join(lines[2:])
        return r

    code_utils.assert_are_equal_ignore_spaces(remove_first_two_lines(xml_str), remove_first_two_lines(expected_xml_str))


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


def test_srcml_repr():
    code = "int a;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    repr_cpp_decl_statement = repr(cpp_decl_statement)
    repr_expected = 'CppDeclStatement(cpp_decls=[CppDecl(cpp_type=CppType(name=\'int\', specifiers=[], modifiers=[]), name=\'a\', init=\'\')])'
    assert repr_cpp_decl_statement == repr_expected


def test_parse_cpp_decl_statement():
    # Basic test
    code = "int a;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    code_utils.assert_are_equal_ignore_spaces(cpp_decl_statement, "int a")

    # # Test with *, initial value and east/west const translation
    code = "int const *a=nullptr;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    code_utils.assert_are_equal_ignore_spaces(cpp_decl_statement, "const int * a = nullptr")

    # Test with several variables + modifiers
    code = "int a = 3, &b = b0, *c;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, """
        int a = 3
        int & b = b0
        int * c
    """)


    # Test with double pointer, which creates a double modifier
    code = "uchar **buffer;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, "uchar * * buffer")

    # Test with a template type
    code = "std::map<int, std::string>x = {1, 2, 3};"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_cpp_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, "std::map<int, std::string> x = {1, 2, 3}")


def test_parse_function_decl():
    # Basic test with repr
    code = "int foo();"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    assert repr(function_decl) == "CppFunctionDecl(type=CppType(name='int', specifiers=[], modifiers=[]), name='foo', parameter_list=CppParameterList(parameters=[]))"

    # Basic test with str
    code = "int foo();"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    assert str(function_decl) == "int foo()"


    # Test with params and default values
    code = "int add(int a, int b = 5);"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "int add(int a, int b = 5)")

    # Test with template types
    code = """
    std::vector<std::pair<size_t, int>>     enumerate(std::vector<int>&   const    xs);
    """
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "std::vector<std::pair<size_t, int>> enumerate(const std::vector<int> & xs)")

    # Test with type declared after ->
    code = "auto divide(int a, int b) -> double;"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "double divide(int a, int b)")


    # Test with inferred type
    code = "auto minimum(int&&a, int b = 5);"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "auto minimum(int && a, int b = 5)")

