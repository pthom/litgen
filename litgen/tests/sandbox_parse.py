import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

from litgen.internal import srcml
from litgen.internal import code_utils, module_pydef_generator
import litgen


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code):
    options = litgen.code_style_imgui()
    cpp_unit = srcml.code_to_cpp_unit(options, code)
    print(cpp_unit)


def play_pydef(code):
    options = litgen.code_style_imgui()
    options.indent_cpp_size = 4
    options.indent_cpp_with_tabs = False
    cpp_unit = srcml.code_to_cpp_unit(options, code)
    pydef_code = litgen.internal.module_pydef_generator.generate_pydef(cpp_unit, options)
    print(f">>>\n{pydef_code}<<<")


def play_imgui():
    options = litgen.code_style_imgui()
    source_filename = os.path.realpath(_THIS_DIR + "/../../../examples_real_libs/imgui/imgui.h")
    cpp_unit = srcml.file_to_cpp_unit(options, source_filename)
    # print(cpp_unit)

#test_code()

#test_imgui()


code = """
        // A dummy structure that likes 
        // to multiply numbers
        struct Multiplier 
        { 
            Multiplier(): factor(0) {} // default constructor
            
            // Constructor with param
            Multiplier(int a, int b): factor(a) {}; 
            
            // Doubles the input number
            int CalculateDouble(int x = 21, int y) 
            { 
                return x * 2; 
            }
            // Who is who?
            int factor = 627;
        };
"""
# play_parse(code)
play_pydef(code)
