import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import code_utils
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot
import function_parser


def test_try_parse_function_name_from_declaration():
    options = code_style_implot()

    def call_parse(code):
        function_parser._SCOPE_OBSERVER.reset()
        pydef = function_parser.try_parse_function_name_from_declaration(code, options)
        assert pydef is not None
        return pydef

    def test_easy():
        code = "IMPLOT_API ImPlotStyle& GetStyle();"
        pydef = call_parse(code)
        assert pydef.name_cpp == "GetStyle"
        assert pydef.return_type_cpp == "ImPlotStyle&"

    test_easy()

    def test_const():
        code = "IMPLOT_API const int& Value();"
        pydef = call_parse(code)
        assert pydef.name_cpp == "Value"
        assert pydef.return_type_cpp == "const int&"

    test_const()

    def test_complex():
        code = """
        IMPLOT_API const std::vector< std::pair<int, float> >    // An annoying comment 
                        *Value(                                  // A annoying * just before the function name
                                const char* fmt, ...);           // and another
        """
        pydef = call_parse(code)
        assert pydef.name_cpp == "Value"
        assert pydef.return_type_cpp == "const std::vector< std::pair<int, float> > *"

    test_complex()



def test_split_function_parameters():
    body = "(int a, ImVec2 c = ImVec2(0,1), int b = 2)"
    items = function_parser._split_function_parameters(body)
    assert str(items) == "['int a', 'ImVec2 c = ImVec2(0,1)', 'int b = 2']"

    body = """(
        const cv::Point2d & zoomCenter,
        double zoomRatio,
        const cv::Size displayedImageSize)"""
    items = function_parser._split_function_parameters(body)
    assert str(items) == "['const cv::Point2d & zoomCenter', 'double zoomRatio', 'const cv::Size displayedImageSize']"

    body = '(ImAxis axis, const char* label = NULL, ImPlotAxisFlags flags = ImPlotAxisFlags_None)'
    items = function_parser._split_function_parameters(body)
    assert str(items) == "['ImAxis axis', 'const char* label = NULL', 'ImPlotAxisFlags flags = ImPlotAxisFlags_None']"


def test_extract_function_parameters():
    code_style_options=  CodeStyleOptions()
    function_decl_body_code = "(const char* name, const ImVec4* cols, int size, bool qual=true)"
    params = function_parser._extract_function_parameters(function_decl_body_code, code_style_options)
    assert str(params) == code_utils.force_one_space("""
            [PydefAttribute(name_cpp='name', type_cpp='const char*', default_value_cpp='', comment_cpp='', line_number=0),
             PydefAttribute(name_cpp='cols', type_cpp='const ImVec4*', default_value_cpp='', comment_cpp='', line_number=0),
             PydefAttribute(name_cpp='size', type_cpp='int', default_value_cpp='', comment_cpp='', line_number=0),
             PydefAttribute(name_cpp='qual', type_cpp='bool', default_value_cpp='true', comment_cpp='', line_number=0)]
    """)


def test_parse_all_functions():
    code = """
// Enables an axis or sets the label and/or flags for an existing axis. Leave #label = NULL for no label.
IMPLOT_API void SetupAxis(ImAxis axis, const char* label = NULL, ImPlotAxisFlags flags = ImPlotAxisFlags_None);
// Sets an axis range limits. If ImPlotCond_Always is used, the axes limits will be locked.
IMPLOT_API void SetupAxisLimits(ImAxis axis, double v_min, double v_max, ImPlotCond cond = ImPlotCond_Once);
// Links an axis range limits to external values. Set to NULL for no linkage. The pointer data must remain valid until EndPlot.
IMPLOT_API void SetupAxisLinks(ImAxis axis, double* link_min, double* link_max);
    """

    options = code_style_implot()
    functions_infos = function_parser.parse_all_function_declarations(code, options)
    assert len(functions_infos) == 3
    assert functions_infos[0].function_code.title_cpp == "Enables an axis or sets the label and/or flags for an existing axis. Leave #label = NULL for no label."
    assert functions_infos[0].function_code.return_type_cpp == "void"
    assert functions_infos[0].function_name_cpp() == "SetupAxis"
    assert functions_infos[0].get_parameters()[0].name_cpp == "axis"
    assert functions_infos[1].get_parameters()[3].default_value_cpp == "ImPlotCond_Once"
    #
    # Much more tests are done in function_generator_tests
    #
