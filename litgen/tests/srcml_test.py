import os, sys;

import pytest

_THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import litgen.internal.srcml as srcml
import litgen.internal.code_utils as code_utils

import logging


def assert_code_unmodified_by_srcml(code: str):
    """
    We transform the code to xml (srcML), and assert that it can safely be translated back to the same code
    """
    root = srcml.code_to_srcml(code)
    code2 = srcml.srcml_to_code(root)
    assert code2 == code


def test_srcml_xml():
    code = "int a = 1"
    element = srcml.code_to_srcml(code, False)
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
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    repr_cpp_decl_statement = repr(cpp_decl_statement)
    repr_expected = "CppDeclStatement(cpp_decls=[CppDecl(cpp_type=CppType(names=['int'], specifiers=[], modifiers=[], argument_list=[]), name='a', init='')])"
    assert repr_cpp_decl_statement == repr_expected


def test_cpp_element_positions():
    code = """
    {
        /* 
        A multiline 
        comment
        */
    }
    """
    element = srcml.first_code_element_with_tag(code, "block")
    cpp_block = srcml.parse_block(element)
    assert str(cpp_block.start) == "2:5"
    assert str(cpp_block.end) == "7:5"


def test_parse_cpp_decl_statement():
    # Basic test
    code = "int a;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    code_utils.assert_are_equal_ignore_spaces(cpp_decl_statement, "int a;")

    # # Test with *, initial value and east/west const translation
    code = "int const *a=nullptr;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    code_utils.assert_are_equal_ignore_spaces(cpp_decl_statement, "const int * a = nullptr;")

    # Test with several variables + modifiers
    code = "int a = 3, &b = b0, *c;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, """
        int a = 3;
        int & b = b0;
        int * c;
    """)


    # Test with double pointer, which creates a double modifier
    code = "uchar **buffer;"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, "uchar * * buffer;")

    # Test with a template type
    code = "std::map<int, std::string>x = {1, 2, 3};"
    element = srcml.first_code_element_with_tag(code, "decl_stmt")
    cpp_decl_statement  = srcml.parse_decl_stmt(element)
    code_utils.assert_are_codes_equal(cpp_decl_statement, "std::map<int, std::string> x = {1, 2, 3};")


def test_parse_function_decl():
    # Basic test with repr
    code = "int foo();"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    assert repr(function_decl) == "CppFunctionDecl(specifiers=[], type=CppType(names=['int'], specifiers=[], modifiers=[], argument_list=[]), name='foo', parameter_list=CppParameterList(parameters=[]), template=None)"

    # Basic test with str
    code = "int foo();"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    assert str(function_decl) == "int foo();"


    # Test with params and default values
    code = "int add(int a, int b = 5);"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "int add(int a, int b = 5);")

    # Test with template types
    code = """
    std::vector<std::pair<size_t, int>>     enumerate(std::vector<int>&   const    xs);
    """
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "std::vector<std::pair<size_t, int>> enumerate(const std::vector<int> & xs);")

    # Test with type declared after ->
    code = "auto divide(int a, int b) -> double;"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "double divide(int a, int b);")


    # Test with inferred type
    code = "auto minimum(int&&a, int b = 5);"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "auto minimum(int && a, int b = 5);")


def test_parse_function_definition():
    code = "int foo() {return 42;}"
    element = srcml.first_code_element_with_tag(code, "function")
    function_srcml  = srcml.parse_function(element)
    function_str = str(function_srcml)
    code_utils.assert_are_codes_equal(function_str, "int foo() { OMITTED_FUNCTION_CODE; }")


def test_nice_warning_message():
    code = """
    void foo(int x, int^ y); // ^ is not an authorized modifier!
    """
    element = srcml.first_code_element_with_tag(code, "function_decl")
    got_exception = False
    try:
        function_srcml  = srcml.parse_function_decl(element)
    except srcml.SrcMlException as e:
        got_exception = True
        message = str(e)

        expected_short_message_on_first_line = 'modifier "^" is not authorized'
        first_message_line = message.splitlines()[0]
        assert expected_short_message_on_first_line in first_message_line

        expected_detailed_infos = [
            "Position:2:21: Issue inside parent cpp_element of type <class 'srcml_types.CppType'> (parsed by litgen.internal.srcml.parse_type)",
            "Issue found in its srcml child, with tag",
            "Parent cpp_element original C++ code:",
            "int^",
            "Parent cpp_element code, as currently parsed by litgen (of type <class 'srcml_types.CppType'>)",
            "Python call stack info",
            ]
        for expected_detailed_info in expected_detailed_infos:
            assert expected_detailed_info in message

    assert got_exception == True


def test_struct_srcml():
    code = """
    struct a {
        int x;
    };
    """
    element = srcml.first_code_element_with_tag(code, "struct", False)
    srcml_str = srcml.srcml_to_str(element)
    expected_str = """
        <?xml version="1.0" ?>
        <ns0:struct
            xmlns:ns0="http://www.srcML.org/srcML/src">
                   struct                    
            <ns0:name>a</ns0:name>
            <ns0:block>
                      {                      
                <ns0:public type="default">
                    <ns0:decl_stmt>
                        <ns0:decl>
                            <ns0:type>
                                <ns0:name>int</ns0:name>
                            </ns0:type>
                            <ns0:name>x</ns0:name>
                        </ns0:decl>
                            ;                         
                    </ns0:decl_stmt>
                </ns0:public>
                      }                   
            </ns0:block>
                   ;                
        </ns0:struct>
        """
    code_utils.assert_are_codes_equal(code_utils.force_one_space(srcml_str), code_utils.force_one_space(expected_str))


def test_srcml_issues_still_present():
    # See issue: https://github.com/srcML/srcML/issues/1687
    code = 'void foo() __attribute__ ((optimize("0")));'
    with pytest.raises(srcml.SrcMlException) as e:
        srcml.parse_code(code)


def verify_code_parse(original_cpp_code, expected_parsed_code = None):
    if expected_parsed_code is None:
        expected_parsed_code = original_cpp_code

    cpp_unit = srcml.parse_code(original_cpp_code)
    cpp_unit_str = str(cpp_unit)
    code_utils.assert_are_codes_equal(cpp_unit_str, expected_parsed_code)


def test_misc_examples():
    verify_code_parse("MY_APY int add();")
    verify_code_parse("int a;")
    verify_code_parse("int v[10];")
    verify_code_parse("const char * const labels[] = NULL;")
    verify_code_parse('void foo() [[gnu::optimize(0)]];', 'void foo();')
    verify_code_parse("void foo(...);")
    verify_code_parse("const Foo & GetFoo() const;")
    verify_code_parse("template<typename T, typename U, int N> void Foo(T x);")
    verify_code_parse("""enum Foo
{
    a = 0,
    b = 1,
};
""")
    verify_code_parse("""template<typename T, typename U, int N>
class Foo
{
        T x = T();
    public:
        std::optional<U> u = std::nullopt;    
        const int n = N;
};""", """template<typename T, typename U, int N>
class Foo
{
    private:
        T x = T();
    public:
        std::optional<U> u = std::nullopt;
        const int n = N;
};
""")

    # Note: lambdas are parsed correctly as decl
    # However, they won't be published in the bindings.
    # Wrap them into published functions if needed
    verify_code_parse("""auto add = [](int a, int b) {
    return a + b;
};
""")


def implot_header_source():
    def preprocess_implot_code(code):
        import re
        new_code = code
        new_code  = re.sub(r'IM_FMTARGS\(\d\)', '', new_code)
        new_code  = re.sub(r'IM_FMTLIST\(\d\)', '', new_code)
        return new_code

    implot_filename = _THIS_DIR + "/../../examples_real_libs/implot/implot.h"
    with open(implot_filename, "r") as f:
        code = f.read()
    return preprocess_implot_code(code)


def test_preprocessor_test_state_and_inclusion_guards():
    code = """
#ifndef MY_HEADER_H
// We are in the main header, and this should be included (the previous ifndef was just an inclusion guard)

void Foo() {}     // This should be included

#ifdef SOME_OPTION
// We are probably entering a zone that handle arcane options and should not be included in the bindings
    void Foo2() {}    // this should be ignored
#else
    void Foo3() {}    // this should be ignored also
#endif // #ifdef SOME_OPTION

#ifndef WIN32
    // We are also probably entering a zone that handle arcane options and should not be included in the bindings
    void Foo4() {}
#endif

#endif // #ifndef MY_HEADER_H    
    """

    parsed_code = srcml.parse_code(code)
    parsed_str = str(parsed_code)
    expected_code = """
// We are in the main header, and this should be included (the previous ifndef was just an inclusion guard)
void Foo() { OMITTED_FUNCTION_CODE; }
// This should be included
// #ifdef SOME_OPTION
// #ifndef MY_HEADER_H
    """
    code_utils.assert_are_codes_equal(parsed_str, expected_code)


def test_parse_implot():
    """This text reads a big header file (+ 1000 lines) and parses it"""
    code = implot_header_source()
    parsed_code = srcml.parse_code(code)
    recomposed_code = str(parsed_code)
    lines = recomposed_code.splitlines()
    assert len(lines) > 1000
