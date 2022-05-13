import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
from litgen.code_generator import perform_generation, remove_all_generated_code, CppCodeType, CodeStyleOptions
from litgen import code_replacements
import os


THIS_DIR = os.path.dirname(__file__)
CPP_HEADERS_DIR = THIS_DIR
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/generated_pybind"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def my_code_style_options():
    options = CodeStyleOptions()
    options.enum_title_on_previous_line = False
    options.generate_to_string = False
    options.functions_namespace = "LiterateGeneratorExample"
    options.indent_size_functions_pydef = 4
    options.functions_api_prefixes = ["MY_API"]
    options.code_replacements = code_replacements.standard_replacements()

    options.buffer_flag_replace_by_array = True
    options.buffer_inner_types = ["T", "void"]
    options.buffer_size_names = ["count"]

    options.function_exclude_regexes = []
    return options


def autogenerate():
    input_header_file =  CPP_HEADERS_DIR + "/litgensample.h"
    dst_file = CPP_GENERATED_PYBIND_DIR + "/pybind_litgensample.cpp"

    # remove_all_generated_code(dst_file)
    # return

    # Configure options
    options = my_code_style_options()

    for code_type in CppCodeType:
        # print(f"{code_type=}")
        perform_generation(
            input_header_file,
            dst_file,
            code_type,
            options)


if __name__ == "__main__":
    print("autogenerate_litgensample")
    autogenerate()
