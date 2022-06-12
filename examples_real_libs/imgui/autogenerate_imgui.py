import os, sys; THIS_DIR = os.path.dirname(__file__); sys.path = [THIS_DIR + "/.."] + sys.path
import litgen
import srcmlcpp

THIS_DIR = os.path.dirname(__file__)
CPP_HEADERS_DIR = THIS_DIR + "/imgui"
CPP_GENERATED_PYBIND_DIR = THIS_DIR + "/bindings"
assert os.path.isdir(CPP_HEADERS_DIR)
assert os.path.isdir(CPP_GENERATED_PYBIND_DIR)


def my_code_style_options():
    options = litgen.code_style_imgui()
    options.original_location_flag_show = True
    return options


def autogenerate():
    input_cpp_header =  CPP_HEADERS_DIR + "/imgui.h"
    output_cpp_module = CPP_GENERATED_PYBIND_DIR + "/pybind_imgui.cpp"
    output_stub_pyi_file = CPP_GENERATED_PYBIND_DIR + "/lg_imgui/__init__.pyi"

    # Configure options
    options = my_code_style_options()

    litgen.generate_files(input_cpp_header=input_cpp_header,
                          output_cpp_module_file=output_cpp_module,
                          options=options,
                          output_stub_pyi_file=output_stub_pyi_file)


if __name__ == "__main__":
    print("autogenerate_imgui")
    autogenerate()
