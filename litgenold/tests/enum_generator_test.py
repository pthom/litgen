import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import enum_generator, enum_parser
from code_types import *
from options import CodeStyleOptions, code_style_implot, code_style_immvision
import code_utils


def test_generate_pydef_enum_cpp_98_code():
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
    generated_code = enum_generator.generate_pydef_enum_cpp_98(enum_infos, options)

    expected_generated_code = """
        py::enum_<ImAxis_>(m, "ImAxis_", py::arithmetic(),
            "Axis indices. The values assigned may change; NEVER hardcode these.")
            // horizontal axes
            .value("X1", ImAxis_X1, "(enabled by default)")
            .value("X2", ImAxis_X2, "(disabled by default)")
            .value("X3", ImAxis_X3, "(disabled by default)")
            // vertical axes
            .value("Y1", ImAxis_Y1, "(enabled by default)")
            .value("Y2", ImAxis_Y2, "(disabled by default)")
            .value("Y3", ImAxis_Y3, "(disabled by default)")
            // bookeeping
        ;
    """
    # Note that the enum value ImAxis_COUNT is intentionally skipped (since it is not useful on python side)
    code_utils.assert_are_codes_equal(expected_generated_code, generated_code)
