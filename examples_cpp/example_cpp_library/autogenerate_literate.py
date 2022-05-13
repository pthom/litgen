import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/../../src_python"] + sys.path
from code_generator import perform_generation, remove_all_generated_code, CppCodeType, code_style_implot
import os

THIS_DIR = os.path.dirname(__file__)
CPP_HEADERS_DIR = THIS_DIR
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/generated_pybind"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def autogenerate():
    input_header_file =  CPP_HEADERS_DIR + "/example_cpp_library.h"
    dst_file = CPP_GENERATED_PYBIND_DIR + "/pybind_example_cpp_library.cpp"

    # remove_all_generated_code(dst_file)
    # return

    # Configure options
    options = code_style_implot()
    options.functions_api_prefixes = "MY_API"

    for code_type in CppCodeType:
        print(f"{code_type=}")
        perform_generation(
            input_header_file,
            dst_file,
            code_type,
            options)


if __name__ == "__main__":
    autogenerate()
