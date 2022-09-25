from typing import List
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


def all_header_files() -> List[str]:
    cpp_headers_dir = THIS_DIR + "/mylib/include/mylib/"
    files = os.listdir(cpp_headers_dir)
    headers = list(filter(lambda f: f.endswith(".h"), files))
    headers_full_path = list(map(lambda f: cpp_headers_dir + f, headers))
    return headers_full_path


def mylib_litgen_options() -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()

    # Generated C++ code style
    options.cpp_indent_size = 4

    # require MY_API for all exported functions
    options.srcml_options.functions_api_prefixes = "MY_API"
    # require MY_API as a suffix for all exported classes, enums, structs and namespaces
    # (i.e. add "// MY_API" as end of line comment)
    options.srcml_options.api_suffixes = "MY_API"

    # Python modifiable immutables options
    options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
        r"^Toggle",
        r"^Modify",
    ]
    options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Change"]

    # c style fixed size array options
    options.fn_params_replace_modifiable_c_array_by_boxed__regexes = ["array", "GetPoints", r"c_string_list_total_size"]

    # c style buffer options (will apply to all functions names, except if containing "Change")
    options.fn_params_replace_buffer_by_array__regex = code_utils.make_regex_exclude_word("Change")

    #
    # Sandbox for other options
    #

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True
    # options.python_max_consecutive_empty_lines = 2
    # options.fn_params_replace_c_string_list__regexes = [
    # options.srcml_options.flag_show_python_callstack = True

    return options


def autogenerate_mylib() -> None:
    print("autogenerate_mylib")
    input_cpp_header = CPP_AMALGAMATED_HEADER
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_mylib.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_mylib/__init__.pyi"
    output_boxed_types_header_file = CPP_GENERATED_PYBIND_DIR + "/mylib_boxed_types.h"

    # Configure options
    options = mylib_litgen_options()

    # We demonstrate here two methods for generating bindings (both of them work correctly):
    # - either using an amalgamated header
    # - or by providing a list of files to litgen
    use_amalgamated_header = True
    if use_amalgamated_header:
        make_testrunner_amalgamated_header()
        generated_code = litgen.generate_code(options, filename=input_cpp_header, add_boxed_types_definitions=True)
    else:
        all_headers = all_header_files()
        files = litgen.CppFilesAndOptionsList()
        for header in all_headers:
            files.files_and_options.append(litgen.CppFileAndOptions(options, filename=header))
        generated_code = litgen.generate_code_for_files(files, add_boxed_types_definitions=True)

    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_module,
        output_stub_pyi_file=output_stub_pyi_file,
        output_boxed_types_header_file=output_boxed_types_header_file,
    )


if __name__ == "__main__":
    autogenerate_mylib()
