import os
import sys

from codemanip import code_utils

import srcmlcpp

import litgen


THIS_DIR = os.path.dirname(__file__)
sys.path = [THIS_DIR + "/.."] + sys.path

THIS_DIR = os.path.dirname(__file__)
CPP_HEADERS_DIR = THIS_DIR + "/example_library"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def my_code_style_options() -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()
    options.cpp_indent_size = 4

    options.srcml_options = srcmlcpp.SrcmlOptions()
    options.srcml_options.functions_api_prefixes = ["MY_API"]

    options.srcml_options.api_suffixes = ["MY_API"]

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True

    # options.python_max_consecutive_empty_lines = 2

    # options.fn_params_replace_c_string_list__regexes = [
    options.fn_params_replace_buffer_by_array__regexes = [code_utils.make_regex_exclude_word("Slider")]
    options.fn_params_replace_modifiable_c_array_by_boxed__regexes = ["array", "GetPoints", r"c_string_list_total_size"]
    options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
        r"^Toggle",
        r"^Modify",
    ]
    options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Slider"]

    return options


def autogenerate() -> None:
    input_cpp_header = CPP_HEADERS_DIR + "/litgensample.h"
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_litgensample.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/litgensample/__init__.pyi"
    output_boxed_types_header_file = CPP_GENERATED_PYBIND_DIR + "/litgensample_boxed_types.h"

    # Configure options
    options = my_code_style_options()

    generated_code = litgen.generate_code(options, filename=input_cpp_header, add_boxed_types_definitions=True)
    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_module,
        output_stub_pyi_file=output_stub_pyi_file,
        output_boxed_types_header_file=output_boxed_types_header_file,
    )


if __name__ == "__main__":
    print("autogenerate_litgensample")
    autogenerate()
