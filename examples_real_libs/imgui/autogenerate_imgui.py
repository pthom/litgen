import copy
import os

import litgen
from litgen.litgen_options_imgui import litgen_options_imgui

THIS_DIR = os.path.dirname(__file__)
print(f"{THIS_DIR=}")
CPP_HEADERS_DIR = THIS_DIR + "/imgui"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def my_code_style_options():
    options = litgen_options_imgui()
    return options


def autogenerate():
    input_cpp_header = CPP_HEADERS_DIR + "/imgui.h"
    input_cpp_header_stdlib = CPP_HEADERS_DIR + "/misc/cpp/imgui_stdlib.h"
    output_cpp_pydef_file = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_imgui/__init__.pyi"
    output_boxed_types_header_file = CPP_GENERATED_PYBIND_DIR + "/imgui_boxed_types.h"

    # Configure options
    options = my_code_style_options()

    options_imgui_h = copy.deepcopy(options)
    options_imgui_h.fn_exclude_by_name__regexes += ["^InputText"]

    # generated_code = litgen.generate_code(options_imgui_h, filename=input_cpp_header, add_boxed_types_definitions=True)

    files_and_options_list = litgen.CppFilesAndOptionsList()
    files_and_options_list.files_and_options = [
        litgen.CppFileAndOptions(options_imgui_h, input_cpp_header),
        litgen.CppFileAndOptions(options, input_cpp_header_stdlib),
    ]
    generated_code = litgen.generate_code_for_files(files_and_options_list, add_boxed_types_definitions=True)

    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        output_boxed_types_header_file=output_boxed_types_header_file,
    )


if __name__ == "__main__":
    print("autogenerate_imgui")

    # import imgui_litgen_patch
    # imgui_litgen_patch.apply_imgui_patch()

    autogenerate()

    # imgui_litgen_patch.revert_imgui_patch()
