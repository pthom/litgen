import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import litgen.internal.srcml as srcml
import litgen.internal.code_utils as code_utils

import logging
import copy


def test_parse_function_decl():
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
    code_utils.assert_are_codes_equal(function_decl, "std::vector<std::pair<size_t, int>>     enumerate(const std::vector<int> &    xs);")

    # Test with type declared after ->
    code = "auto divide(int a, int b) -> double;"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "auto divide(int a, int b) -> double;")


    # Test with inferred type
    code = "auto minimum(int&&a, int b = 5);"
    element = srcml.first_code_element_with_tag(code, "function_decl")
    function_decl  = srcml.parse_function_decl(element)
    code_utils.assert_are_codes_equal(function_decl, "auto minimum(int &&a, int b = 5);")


def test_parse_function_definition():
    code = "int foo() {return 42;}"
    element = srcml.first_code_element_with_tag(code, "function")
    function_srcml  = srcml.parse_function(element)
    function_str = str(function_srcml)
    code_utils.assert_are_codes_equal(function_str, "int foo() {return 42;}")



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


def do_parse_imgui_implot(filename):
    options_backup = copy.deepcopy(srcml.OPTIONS)
    srcml.OPTIONS = srcml.SrmlCppOptions.options_litgen_imgui_implot()
    srcml.OPTIONS.flag_quiet = True
    parsed_code = srcml.parse_file(filename)
    srcml.OPTIONS = options_backup
    recomposed_code = str(parsed_code)
    lines = recomposed_code.splitlines()
    assert len(lines) > 500


def test_parse_imgui():
    source_filename = _THIS_DIR + "/../../examples_real_libs/imgui/imgui.h"
    do_parse_imgui_implot(source_filename)


def test_parse_implot():
    source_filename = _THIS_DIR + "/../../examples_real_libs/implot/implot.h"
    do_parse_imgui_implot(source_filename)
