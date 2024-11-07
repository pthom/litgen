from __future__ import annotations
import os

from codemanip import amalgamated_header, code_utils
from srcmlcpp.scrml_warning_settings import WarningType
import litgen
from litgen import litgen_generator


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CPP_AMALGAMATED_HEADER = THIS_DIR + "/mylib_amalgamation/mylib_amalgamation.h"


def pydef_fname(bind_library_type: litgen.BindLibraryType) -> str:
    if bind_library_type == litgen.BindLibraryType.pybind11:
        return "/pybind_mylib.cpp"
    else:
        return "/nanobind_mylib.cpp"


def pydef_dir(bind_library_type: litgen.BindLibraryType) -> str:
    if bind_library_type == litgen.BindLibraryType.pybind11:
        return THIS_DIR + "/_pydef_pybind11"
    else:
        return THIS_DIR + "/_pydef_nanobind"


def stubs_dir(_bind_library_type: litgen.BindLibraryType) -> str:
    return THIS_DIR + "/_stubs/lg_mylib"


def write_mylib_amalgamation() -> None:
    options = amalgamated_header.AmalgamationOptions()
    options.base_dir = THIS_DIR
    options.local_includes_startwith = "mylib/"
    # options.include_subdirs = ["."]
    options.main_header_file = "mylib/mylib_main/mylib.h"
    options.dst_amalgamated_header_file = CPP_AMALGAMATED_HEADER

    amalgamated_header.write_amalgamate_header_file(options)


def all_header_files() -> list[str]:
    cpp_headers_dir = THIS_DIR + "/mylib/include/mylib/"
    files = os.listdir(cpp_headers_dir)
    headers = list(filter(lambda f: f.endswith(".h"), files))
    headers_full_path = list(map(lambda f: cpp_headers_dir + f, headers))
    return headers_full_path


def mylib_litgen_options(bind_library_type: litgen.BindLibraryType) -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.ignored_warnings = [
        WarningType.LitgenClassMemberNonNumericCStyleArray,
        WarningType.LitgenIgnoreElement,
    ]
    options.bind_library = bind_library_type

    options.python_run_black_formatter = True

    # Generated C++ code style
    options.cpp_indent_size = 4

    # require MY_API for all exported functions
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    options.fn_exclude_non_api = True

    options.class_exclude_by_name__regex = "Detail$"
    options.enum_exclude_by_name__regex = "Detail$"

    # For smart_ptr_test: SmartElem will be held in (vector of) shared_ptr
    options.class_held_as_shared__regex = "^SmartElem$"

    # Python modifiable immutables options
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = code_utils.join_string_by_pipe_char(
        [
            r"^Toggle",
            r"^Modify",
        ]
    )
    options.fn_params_output_modifiable_immutable_to_return__regex = r"^Change"

    options.fn_return_force_policy_reference_for_references__regex = r"instance"

    # c style fixed size array options
    options.fn_params_replace_c_array_modifiable_by_boxed__regex = code_utils.join_string_by_pipe_char(
        ["array", "GetPoints", r"c_string_list_total_size"]
    )

    # c style buffer options (will apply to all functions names, except if containing "Change")
    options.fn_params_replace_buffer_by_array__regex = code_utils.make_regex_exclude_word("Change")

    # namespace
    options.namespaces_root = ["Mylib"]

    options.class_expose_protected_methods__regex = "^MyVirtual"
    options.class_override_virtual_methods_in_python__regex = "^MyVirtual"

    options.fn_namespace_vectorize__regex = r"^MathFunctions$"
    options.fn_vectorize__regex = r".*"

    options.fn_params_replace_buffer_by_array__regex = r".*"
    # options.fn_vectorize_suffix = "_vectorized"

    options.class_dynamic_attributes__regex = r"Dynamic$"

    options.fn_template_options.add_specialization(
        r"^AddTemplated$",
        ["int", "double", "std::string"],
        add_suffix_to_function_name=False,
    )
    options.fn_template_options.add_specialization(
        r"^SumVector",
        ["int", "std::string"],
        add_suffix_to_function_name=True,
    )

    options.class_template_options.add_specialization(
        name_regex=r"^MyTemplateClass$",  # r".*" => all classes
        cpp_types_list_str=["int", "std::string"],  # instantiated types
        cpp_synonyms_list_str=[],
    )

    options.class_deep_copy__regex = r"^Copyable_"
    options.class_copy__regex = r"^Copyable_"
    options.class_template_options.add_specialization(
        name_regex=r"^Copyable_",  # r".*" => all classes
        cpp_types_list_str=["int"],  # instantiated types
        cpp_synonyms_list_str=[],
    )

    options.macro_define_include_by_name__regex = r"^MY_"
    options.macro_name_replacements.add_first_replacement("MY_", "")

    # pybind11 supports bindings for multiple inheritance, nanobind does not
    if bind_library_type == litgen.BindLibraryType.pybind11:
        options.srcmlcpp_options.header_filter_acceptable__regex += "|BINDING_MULTIPLE_INHERITANCE"

    #
    # Sandbox for other options
    #

    # options.original_location_flag_show = True
    # options.original_location_nb_parent_folders = 0
    # options.original_signature_flag_show = True
    # options.python_run_black_formatter = True
    # options.srcmlcpp_options.flag_show_python_callstack = True

    return options


def autogenerate_mylib(bind_library_type: litgen.BindLibraryType) -> None:
    _pydef_dir = pydef_dir(bind_library_type)
    _stubs_dir = stubs_dir(bind_library_type)
    output_cpp_module = _pydef_dir + pydef_fname(bind_library_type)
    output_stub_pyi_file = _stubs_dir + "/__init__.pyi"

    # Configure options
    options = mylib_litgen_options(bind_library_type)

    # We demonstrate here two methods for generating bindings (both of them work correctly):
    # - either using an amalgamated header
    # - or by providing a list of files to litgen
    use_amalgamated_header = True
    if use_amalgamated_header:
        write_mylib_amalgamation()
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


def save_all_generated_codes_by_file(bind_library_type: litgen.BindLibraryType) -> None:
    """This is specific to litgen's integration tests.
    It will generate all the files xxx_test.h.pydef.cpp and xxx_test.h.pyi
    :return:
    """
    options = mylib_litgen_options(bind_library_type)
    headers_dir = THIS_DIR + "/mylib/"

    def process_one_file(header_file: str) -> None:
        # print(header_file)
        input_cpp_header_file = headers_dir + header_file
        if bind_library_type == litgen.BindLibraryType.pybind11:
            output_cpp_pydef_file = input_cpp_header_file + ".pydef.cpp"
        else:
            output_cpp_pydef_file = input_cpp_header_file + ".pydef_nano.cpp"
        output_stub_pyi_file = input_cpp_header_file + ".pyi"

        if not os.path.isfile(output_cpp_pydef_file):
            with open(output_cpp_pydef_file, "w") as f:
                f.write(pydef_template_code(bind_library_type, header_file))
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


def pydef_template_code(bind_library_type: litgen.BindLibraryType, header_filename: str) -> str:
    if bind_library_type == litgen.BindLibraryType.pybind11:
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
            #include "mylib_main/mylib.h"

            namespace py = pybind11;

            // <litgen_glue_code>  // Autogenerated code below! Do not edit!
            // </litgen_glue_code> // Autogenerated code end


            void py_init_module_mylib(py::module& m)
            {{
                // <litgen_pydef> // Autogenerated code below! Do not edit!
                // </litgen_pydef> // Autogenerated code end
            }}
    """
    else:
        code = f"""
            // ============================================================================
            // This file was autogenerated
            // It is presented side to side with its source: {header_filename}
            // It is not used in the compilation
            //    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
            //     code, including this code)
            // ============================================================================

            #include <nanobind/nanobind.h>
            #include <nanobind/stl/string.h>
            #include <nanobind/stl/function.h>
            #include "mylib_main/mylib.h"

            namespace nb = nanobind;

            // <litgen_glue_code>  // Autogenerated code below! Do not edit!
            // </litgen_glue_code> // Autogenerated code end


            void py_init_module_mylib(nb::module_& m)
            {{
                // <litgen_pydef> // Autogenerated code below! Do not edit!
                // </litgen_pydef> // Autogenerated code end
            }}
    """
    code = code_utils.unindent_code(code, flag_strip_empty_lines=True) + "\n"

    if bind_library_type == litgen.BindLibraryType.nanobind:
        code = code.replace("<pybind11", "<nanobind")
        code = code.replace("pybind11.h", "nanobind.h")

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

# <litgen_stub> // Autogenerated code below! Do not edit!
# </litgen_stub> // Autogenerated code end!
"""[
        1:
    ]
    return code


def main() -> None:
    generate_file_by_file = True
    import sys

    if "no_generate_file_by_file" in sys.argv:
        generate_file_by_file = False

    lib_types = []
    if "pybind" in sys.argv:
        lib_types.append(litgen.BindLibraryType.pybind11)
    if "nanobind" in sys.argv:
        lib_types.append(litgen.BindLibraryType.nanobind)
    if not lib_types:
        # No flavor specified, generate both
        lib_types = [
            litgen.BindLibraryType.nanobind,
            litgen.BindLibraryType.pybind11,
        ]

    print("autogenerate_mylib ...", end="\r")
    for bind_library_type in lib_types:
        print("autogenerate_mylib for ", bind_library_type)
        autogenerate_mylib(bind_library_type)
        if generate_file_by_file:
            save_all_generated_codes_by_file(bind_library_type)
    print("autogenerate_mylib done")


if __name__ == "__main__":
    main()
