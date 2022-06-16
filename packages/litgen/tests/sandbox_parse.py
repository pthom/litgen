import os, sys

_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")

import srcmlcpp
from srcmlcpp import srcml_main
from litgen.internal import code_utils, module_pydef_generator
import litgen


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = litgen.code_style_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    print(cpp_unit)


def play_imgui():
    options = litgen.code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)


def play_implot():
    options = litgen.code_style_implot()
    options.original_location_flag_show = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)
    pydef_code = module_pydef_generator.generate_pydef(cpp_unit, options)
    print(pydef_code)


def play_pydef(code, options):
    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # # print(srcml_utils.srcml_to_str_readable(xml))
    # print(srcml_utils.srcml_to_str(xml))

    pydef_code = litgen.generate_pydef(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pydef_code}<<<")


# test_code()


def play_pyi(code, options):
    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code, dump_positions=False)
    # # print(srcml_utils.srcml_to_str_readable(xml))
    # print(srcml_utils.srcml_to_str(xml))

    pyi_code = litgen.generate_pyi(code, options, add_boxed_types_definitions=True)
    print(f">>>\n{pyi_code}<<<")


# options = litgen.options.code_style_implot()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
# options.srcml_options.api_suffixes = ["MY_API"]

options = litgen.options.CodeStyleOptions()
options.srcml_options.functions_api_prefixes = ["MY_API"]

# options = litgen.code_style_imgui()

options.original_location_flag_show = True


code = """
MY_API inline int buffer_sum(const uint8_t* buffer, size_t buffer_size, size_t stride= sizeof(uint8_t));
"""

# play_pydef(code, options)
play_pyi(code, options)
