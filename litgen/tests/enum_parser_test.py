import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot
import find_functions_structs_enums
import enum_parser


def test_parse_all_enum_cpp_98():
    code = """
// Axis indices. The values assigned may change; NEVER hardcode these.
enum ImAxis_ {
    // horizontal axes
    ImAxis_X1 = 0, // enabled by default
    ImAxis_X2,     // disabled by default
    ImAxis_X3,     // disabled by default
    // vertical axes
    ImAxis_Y1,     // enabled by default
    ImAxis_Y2,     // disabled by default
    ImAxis_Y3,     // disabled by default
    // bookeeping
    ImAxis_COUNT
};
    """

    options = code_style_implot()
    enums_infos = enum_parser.parse_all_enum_cpp_98(code, options)
    assert len(enums_infos) == 1
    enum_infos = enums_infos[0]
    assert enum_infos.get_attr_and_regions()[0].code_region_comment is not None
    assert enum_infos.get_attr_and_regions()[0].code_region_comment.comment_cpp == "horizontal axes"

    assert enum_infos.get_attr_and_regions()[1].enum_cpp_98_value.name_cpp == "ImAxis_X1"

    assert enum_infos.get_attr_and_regions()[2].enum_cpp_98_value.name_cpp == "ImAxis_X2"
    #
    # Much more tests are done in enum_generator_tests,
    # which in turn will invoke parse_all_enum_cpp_98
    # and serve as tests for this module
    #
