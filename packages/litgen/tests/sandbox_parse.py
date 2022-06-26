import os
import sys

import srcmlcpp

import litgen
from litgen.litgen_options_imgui import litgen_options_imgui
from litgen.litgen_options_implot import litgen_options_implot


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = litgen_options_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    print(cpp_unit)


def play_implot():
    options = litgen_options_implot()
    options.original_location_flag_show = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")

    generated_code = litgen.code_to_pydef(options, filename=source_filename)
    print(generated_code)


def play_imgui():
    options = litgen_options_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")

    generated_code = litgen.code_to_pydef(options, filename=source_filename)
    print(generated_code)


def play_stub(code, options) -> None:
    pyi_code = litgen.code_to_stub(options, code)
    print(f">>>\n{pyi_code}<<<")


def play_pydef(code, options) -> None:
    pyi_code = litgen.code_to_pydef(options, code)
    print(f">>>\n{pyi_code}<<<")


code = """
struct Foo
{
    std::string foo();
    std::string foo(int a);
    void blah();
};
"""
options = litgen.options.LitgenOptions()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
options.original_location_flag_show = True
options.original_signature_flag_show = True
# options = code_style_imgui()

# play_stub(code, options)
play_pydef(code, options)


from typing import Mapping

a = [1, 2, 3]


def square(x: int) -> int:
    return x * x


b: map[int] = map(square, a)
