import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
import litgen

THIS_DIR = os.path.dirname(__file__)
CPP_HEADERS_DIR = THIS_DIR + "/example_library"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def my_code_style_options():
    options = litgen.CodeStyleOptions()
    options.enum_title_on_previous_line = False
    options.generate_to_string = False
    options.indent_size_cpp_pydef = 4
    options.functions_api_prefixes = ["MY_API"]
    options.struct_api_suffixes = ["MY_API_STRUCT"]
    options.function_exclude_by_comment = ["MY_API_EXCLUDE"]
    options.code_replacements = litgen.standard_replacements()

    options.buffer_flag_replace_by_array = True

    options.function_name_exclude_regexes = []
    options.functions_api_prefixes
    return options


def autogenerate():
    input_cpp_header =  CPP_HEADERS_DIR + "/litgensample.h"
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_litgensample.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/litgensample/__init__.pyi"

    # Configure options
    options = my_code_style_options()

    litgen.generate(input_cpp_header=input_cpp_header,
                    output_cpp_module_file=output_cpp_module,
                    options=options,
                    output_stub_pyi_file=output_stub_pyi_file)


if __name__ == "__main__":
    print("autogenerate_litgensample")
    autogenerate()
