import os
import sys

import srcmlcpp

import litgen
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


def play_implot():
    options = code_style_implot()
    options.original_location_flag_show = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")

    generated_code = litgen.generate_code(options, filename=source_filename)
    print(generated_code.pydef_code)


def play_imgui():
    options = code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")

    generated_code = litgen.generate_code(options, filename=source_filename)
    print(generated_code.pydef_code)


def play_stub(code, options) -> None:
    pyi_code = litgen.code_to_stub(options, code)
    print(f">>>\n{pyi_code}<<<")


def play_pydef(code, options) -> None:
    pyi_code = litgen.code_to_pydef(options, code)
    print(f">>>\n{pyi_code}<<<")


code = """
    // Returns the sum of a const buffer
    MY_API inline int buffer_sum(const uint8_t* buffer, size_t buffer_size, size_t stride= sizeof(uint8_t))
    {
        int sum = 0;
        for (size_t i  = 0; i < buffer_size; ++i)
            sum += (int)buffer[i];
        return sum;
    }
"""
options = litgen.options.LitgenOptions()
options.srcml_options.functions_api_prefixes = ["MY_API"]
# options.original_location_flag_show = True
# options = code_style_imgui()

# play_stub(code, options)
play_pydef(code, options)
