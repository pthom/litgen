import os
import sys

import srcmlcpp

import litgen
from litgen.internal import module_pydef_generator
from litgen.options import code_style_imgui, code_style_implot


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = code_style_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    print(cpp_unit)


def play_imgui():
    options = code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)


def play_implot():
    options = code_style_implot()
    options.original_location_flag_show = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)
    pydef_code = module_pydef_generator.generate_pydef(cpp_unit, options)
    print(pydef_code)


def play_pydef(code, options) -> None:
    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # # print(srcml_utils.srcml_to_str_readable(xml))
    # print(srcml_utils.srcml_to_str(xml))

    pydef_code = litgen.generate_pydef(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pydef_code}<<<")


# test_code()


def play_stub(code, options):
    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # # print(srcml_utils.srcml_to_str_readable(xml))
    # print(srcml_utils.srcml_to_str(xml))

    pyi_code = litgen.generate_stub(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pyi_code}<<<")


# options = litgen.options.code_style_implot()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
# options.srcml_options.api_suffixes = ["MY_API"]

options = litgen.options.LitgenOptions()
options.srcml_options.functions_api_prefixes = ["MY_API"]

# options = litgen.code_style_imgui()

options.original_location_flag_show = True


code = """
struct BoxedUnsignedLong // MY_API
{
    unsigned long value;
    BoxedUnsignedLong() : value{} {}
    BoxedUnsignedLong(unsigned long v) : value(v) {}
    std::string __repr__() const { return std::string("BoxedUnsignedLong(") + std::to_string(value) + ")"; }
};

struct BoxedInt // MY_API
{
    int value;
    BoxedInt() : value{} {}
    BoxedInt(int v) : value(v) {}
    std::string __repr__() const { return std::string("BoxedInt(") + std::to_string(value) + ")"; }
};
"""

play_pydef(code, options)
# play_stub(code, options)
