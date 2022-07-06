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


def litgensample_options() -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()
    # options.fn_params_replace_buffer_by_array__regexes = [r".*"]
    # options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [r"^Toggle", r"^Modify"]
    # options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Slider"]

    options.fn_params_replace_modifiable_c_array_by_boxed__regexes = ["array"]
    options.fn_params_output_modifiable_immutable_to_return__regexes = [r".*"]
    return options


code = """
enum Foo
{
    Foo_A,
    Foo_B,
    Foo_Count
};

void PlayFoo(Foo f = Foo_A);
"""
# options = litgen_options_imgui()
options = litgen.options.LitgenOptions()
# options.fn_params_replace_modifiable_c_array_by_boxed__regexes = []
# # options.fn_params_replace_const_c_array_by_std_array__regexes = []
# options.fn_params_output_modifiable_immutable_to_return__regexes = [r".*"]
# play_stub(code, options)
play_stub(code, options)
