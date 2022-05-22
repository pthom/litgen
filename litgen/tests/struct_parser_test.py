import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import code_utils
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot
import struct_parser
import find_functions_structs_enums


def test_try_parse_struct_declaration():
    """
    Accepts lines like
        struct ImPlotContext {
    or
        struct ImPlotContext
        {
    but refuses forward declarations like
        struct ImPlotContext;             // ImPlot context (opaque struct, see implot_internal.h)
    """

    options = code_style_implot()

    line = "struct ImPlotContext {"
    pydef = struct_parser._try_parse_struct_declaration(line, options)
    assert pydef.name_cpp == "ImPlotContext"

    line = "struct ImPlotContext; {"
    pydef = struct_parser._try_parse_struct_declaration(line, options)
    assert pydef is None


def test_try_parse_attribute():
    def test_ifdef():
        state = struct_parser._ParseScopeObserver()
        line_number = 22

        code_line = "#ifdef TRUC"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 0
        assert state._nb_ifdef_zone == 1

        code_line = "double x = 0;"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 0

        code_line = "#endif // #ifdef TRUC"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 0
        assert state._nb_ifdef_zone == 0

        code_line = "double x = 1;"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 1
        assert state._nb_ifdef_zone == 0
    test_ifdef()

    def test_easy():
        state = struct_parser._ParseScopeObserver()
        code_line = "double xStart = 1; // X comment   "
        line_number = 22
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 1
        attr = attrs[0]
        assert attr.docstring_cpp == "X comment"
        assert attr.line_number == 22
        assert attr.name_cpp == "xStart"
        assert attr.type_cpp == "double"
        assert attr.default_value_cpp == "1"
    test_easy()

    def test_no_default_value():
        state = struct_parser._ParseScopeObserver()
        code_line = "std::vector <cv::Point> WatchedPixels; // std::vector <cv::Point> is empty by default   "
        line_number = 22
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 1
        attr = attrs[0]
        assert attr.type_cpp == "std::vector <cv::Point>"
        assert attr.docstring_cpp == "std::vector <cv::Point> is empty by default"
        assert attr.default_value_cpp == ""
    test_no_default_value()

    def test_default_value_with_parenthesis():
        state = struct_parser._ParseScopeObserver()
        code_line = "std::vector <cv::Point> WatchedPixels = std::vector-<cv::Point>() // is empty by default   "
        line_number = 22
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 1
        attr = attrs[0]
        assert attr.default_value_cpp == "std::vector-<cv::Point>()"
    test_default_value_with_parenthesis()

    def test_multiple_attributes():
        state = struct_parser._ParseScopeObserver()
        code_line = "double xStart, yStart, zStart\t, wStart = 0.1; // Comment"
        line_number = 22
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 4
        assert attrs[0].name_cpp == "xStart"
        assert attrs[0].type_cpp == "double"
        assert attrs[0].default_value_cpp == "0.1"
    test_multiple_attributes()

    def test_method_declaration():
        state = struct_parser._ParseScopeObserver()
        line_number = 22

        code_line = "bool Contains(const ImPlotPoint& p) const; // comment"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 0

        code_line = "Rect rect = ImPlotRect(); // comment"
        attrs = struct_parser._try_parse_struct_member(state, line_number, code_line)
        assert len(attrs) == 1
        assert attrs[0].default_value_cpp == "ImPlotRect()"
    test_method_declaration()


def test_parse_struct_pydef():
    options = code_style_implot()


    code = """
    struct Foo 
    {
        int i = 0;
    };
    """
    struct_infos = struct_parser.parse_one_struct_testonly(code, options)
    assert struct_infos.struct_name() == "Foo"
    assert len(struct_infos.get_attr_and_regions()) == 1
