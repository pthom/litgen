from typing import List
import os
from codemanip import code_utils

import litgen
from codemanip.make_amalgamated_header import (
    AmalgamationOptions,
    write_amalgamate_header_file,
)
from litgen import litgen_generator

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

    options.python_run_black_formatter = True

    # Generated C++ code style
    options.cpp_indent_size = 4

    # require MY_API for all exported functions
    options.srcml_options.functions_api_prefixes = "MY_API"
    options.fn_exclude_non_api = True

    options.class_exclude_by_name__regex = "Detail$"
    options.enum_exclude_by_name__regex = "Detail$"

    # Python modifiable immutables options
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = code_utils.join_string_by_pipe_char(
        [
            r"^Toggle",
            r"^Modify",
        ]
    )
    options.fn_params_output_modifiable_immutable_to_return__regex = r"^Change"

    # c style fixed size array options
    options.fn_params_replace_c_array_modifiable_by_boxed__regex = code_utils.join_string_by_pipe_char(
        ["array", "GetPoints", r"c_string_list_total_size"]
    )

    # c style buffer options (will apply to all functions names, except if containing "Change")
    options.fn_params_replace_buffer_by_array__regex = code_utils.make_regex_exclude_word("Change")

    # namespace
    options.namespace_root__regex = "Mylib"

    options.class_expose_protected_methods__regex = "^MyVirtual"
    options.class_override_virtual_methods_in_python__regex = "^MyVirtual"

    options.fn_namespace_vectorize__regex = r"^MathFunctions$"
    options.fn_vectorize__regex = r".*"
    # options.fn_vectorize_suffix = "_vectorized"

    options.class_dynamic_attributes__regex = r"Dynamic$"

    options.fn_template_options.add_specialization(r"^AddTemplated$", ["int", "double", "std::string"])
    options.fn_template_options.add_specialization(r"^SumVector", ["int", "std::string"])

    options.class_template_options.add_specialization(
        class_name_regex=r"^MyTemplateClass$",  # r".*" => all classes
        cpp_types_list=["int", "std::string"],  # instantiated types
        naming_scheme=litgen.TemplateNamingScheme.camel_case_suffix,
    )

    #
    # Sandbox for other options
    #

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True
    # options.srcml_options.flag_show_python_callstack = True

    return options


def autogenerate_mylib() -> None:

    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_mylib.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_mylib/__init__.pyi"

    # Configure options
    options = mylib_litgen_options()

    # We demonstrate here two methods for generating bindings (both of them work correctly):
    # - either using an amalgamated header
    # - or by providing a list of files to litgen
    use_amalgamated_header = True
    if use_amalgamated_header:
        make_testrunner_amalgamated_header()
        litgen_generator.write_generated_code_for_file(
            options,
            CPP_AMALGAMATED_HEADER,
            output_cpp_module,
            output_stub_pyi_file,
        )
    else:
        litgen_generator.write_generated_code_for_files(
            options,
            all_header_files(),
            output_cpp_module,
            output_stub_pyi_file,
        )


def save_all_generated_codes_by_file():
    options = mylib_litgen_options()
    headers_dir = THIS_DIR + "/mylib/include/mylib/"

    def process_one_file(header_file: str):
        # print(header_file)
        input_cpp_header_file = headers_dir + header_file
        output_cpp_pydef_file = input_cpp_header_file + ".pydef.cpp"
        output_stub_pyi_file = input_cpp_header_file + ".pyi"

        if not os.path.isfile(output_cpp_pydef_file):
            with open(output_cpp_pydef_file, "w") as f:
                f.write(pydef_template_code(header_file))
        if not os.path.isfile(output_stub_pyi_file):
            with open(output_stub_pyi_file, "w") as f:
                f.write(stub_template_code(header_file))

        litgen.write_generated_code_for_file(
            options,
            input_cpp_header_file=input_cpp_header_file,
            output_cpp_pydef_file=output_cpp_pydef_file,
            output_stub_pyi_file=output_stub_pyi_file,
        )

    for f in os.listdir(headers_dir):
        if f.endswith(".h"):
            process_one_file(f)


def pydef_template_code(header_filename: str) -> str:
    code = f"""
// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: {header_filename}
// It is not used in the compilation
//    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
//     code, including this code)
// ============================================================================

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include "mylib/mylib.h"

namespace py = pybind11;

// <litgen_glue_code>  // Autogenerated code below! Do not edit!
// </litgen_glue_code> // Autogenerated code end


void py_init_module_mylib(py::module& m)
{{
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    // </litgen_pydef> // Autogenerated code end
}}
"""[
        1:
    ]
    return code


def stub_template_code(header_filename: str) -> str:
    code = f"""
# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: {header_filename}
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore
import sys
from typing import Literal, List, Any, Optional, Tuple, Dict
import numpy as np
from enum import Enum, auto
import numpy

# <litgen_stub> // Autogenerated code below! Do not edit!
# </litgen_stub> // Autogenerated code end!
    """[
        1:
    ]
    return code


if __name__ == "__main__":
    print("autogenerate_mylib ...", end="\r")
    autogenerate_mylib()
    save_all_generated_codes_by_file()
    print("autogenerate_mylib done")
