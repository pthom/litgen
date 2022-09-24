import os
from codemanip import code_utils

import litgen
from litgen.make_amalgamated_header import AmalgamationOptions, write_amalgamate_header_file


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CPP_LIB_DIR = THIS_DIR + "/mylib"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
CPP_AMALGAMATED_HEADER = THIS_DIR + "/mylib_amalgamation/mylib_amalgamation.h"


def make_testrunner_amalgamated_header() -> None:
    options = AmalgamationOptions()
    options.base_dir = CPP_LIB_DIR
    options.local_includes_startwith = "mylib/"
    options.include_subdirs = ["include"]
    options.main_header_file = "mylib/mylib.h"
    options.dst_amalgamated_header_file = CPP_AMALGAMATED_HEADER

    write_amalgamate_header_file(options)


def my_code_style_options() -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()

    # Generated C++ code style
    options.cpp_indent_size = 4

    # require MY_API for all exported functions
    options.srcml_options.functions_api_prefixes = ["MY_API"]
    # require MY_API for all exported classes, enums, structs and namespaces (add // MY_API as eol comment)
    options.srcml_options.api_suffixes = ["MY_API"]

    # Python modifiable immutables options
    options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
        r"^Toggle",
        r"^Modify",
    ]
    options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Change"]

    # c style fixed size array options
    options.fn_params_replace_modifiable_c_array_by_boxed__regexes = ["array", "GetPoints", r"c_string_list_total_size"]

    # c style buffer options (will apply to all functions names, except if containing "Change")
    options.fn_params_replace_buffer_by_array__regexes = [code_utils.make_regex_exclude_word("Change")]

    #
    # Sandbox for other options
    #

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True
    # options.python_max_consecutive_empty_lines = 2
    # options.fn_params_replace_c_string_list__regexes = [

    return options


def autogenerate_testrunner() -> None:
    input_cpp_header = CPP_AMALGAMATED_HEADER
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_mylib.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_mylib/__init__.pyi"
    output_boxed_types_header_file = CPP_GENERATED_PYBIND_DIR + "/mylib_boxed_types.h"

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
    print("autogenerate_testrunner")
    make_testrunner_amalgamated_header()
    autogenerate_testrunner()
