import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")

import srcmlcpp
from srcmlcpp import srcml_main
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

    # from srcmlcpp import srcml_utils
    # xml = srcmlcpp.code_to_srcml(code)
    # print(srcml_utils.srcml_to_str_readable(xml))

    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    pydef_code = litgen.internal.module_pydef_generator.generate_pydef(cpp_unit, options)
    print(f">>>\n{pydef_code}<<<")


def play_imgui():
    options = litgen.code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/imgui/imgui/imgui.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)

def play_implot():
    options = litgen.code_style_implot()
    options.flag_show_original_location_in_pybind_file = True
    source_filename = os.path.realpath(_THIS_DIR + "/../../examples_real_libs/implot/implot/implot.h")
    cpp_unit = srcmlcpp.file_to_cpp_unit(options.srcml_options, source_filename)
    # print(cpp_unit)
    pydef_code = module_pydef_generator.generate_pydef(cpp_unit, options)
    print(pydef_code)


#test_code()


# IMGUI_API bool          Combo(const char* label, int* current_item, const char* const items[], int items_count);
# options = code_style_implot()
# options.srcml_options.functions_api_prefixes = ["MY_API"]
code = """
inline void change_c_array(unsigned long values[2]);
"""
# play_parse(code)
play_pydef(code)
# play_imgui()

# play_implot()