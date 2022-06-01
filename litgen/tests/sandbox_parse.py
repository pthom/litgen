import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")

import srcmlcpp
from litgen.internal import code_utils, module_pydef_generator
import litgen


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = litgen.code_style_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    print(cpp_unit)


def play_pydef(code):
    options = litgen.options.code_style_implot()
    options.srcml_options.functions_api_prefixes = ["MY_API"]
    options.indent_cpp_size = 4
    options.indent_cpp_with_tabs = False
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    pydef_code = litgen.internal.module_pydef_generator.generate_pydef(cpp_unit, options)
    print(f">>>\n{pydef_code}<<<")


def play_imgui():
    options = litgen.code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../../examples_real_libs/imgui/imgui.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options, source_filename)
    # print(cpp_unit)

#test_code()

#test_imgui()


# options = code_style_implot()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
code = """
            MY_API template<typename T> inline int test_with_two_template_buffers(const T* values1, T* values2, int count);
"""
# play_parse(code)
play_pydef(code)
