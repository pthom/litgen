import os
import sys

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

    options.buffer_flag_replace_by_array = True

    options.srcml_options.function_name_exclude_regexes = []

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True
    # options.python_black_formatter_line_length = 60

    # options.python_max_consecutive_empty_lines = 2

    return options


def autogenerate() -> None:
    input_cpp_header = CPP_HEADERS_DIR + "/litgensample.h"
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_litgensample.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/litgensample/__init__.pyi"
    output_boxed_types_header_file = CPP_GENERATED_PYBIND_DIR + "/litgensample_boxed_types.h"

    # Configure options
    options = my_code_style_options()

    litgen.write_generated_code(
        options=options,
        input_cpp_header=input_cpp_header,
        output_cpp_pydef_file=output_cpp_module,
        output_stub_pyi_file=output_stub_pyi_file,
        output_boxed_types_header_file=output_boxed_types_header_file,
        add_boxed_types_definitions=True,
    )


if __name__ == "__main__":
    print("autogenerate_litgensample")
    autogenerate()
