import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

_THIS_DIR = "/Users/pascal/dvp/OpenSource/ImGuiWork/litgen/litgen/tests/"

import litgen.internal.srcml as srcml
import litgen.internal.code_utils as code_utils


def read_file_content(filename):
    with open(filename, "r") as f:
        content = f.read()
    return content


def do_parse_imgui_implot(filename):

    srcml.OPTIONS = srcml.SrmlCppOptions.options_litgen_imgui_implot()

    # srcml.OPTIONS = srcml.SrmlCppOptions.options_preserve_code()
    # srcml.OPTIONS.code_preprocess_function = srcml._preprocess_imgui_code

    srcml.OPTIONS.flag_short_message = True

    parsed_code = srcml.parse_file(filename)
    recomposed_code = str(parsed_code)
    lines = recomposed_code.splitlines()
    print(recomposed_code)


def test_parse_implot():
    do_parse_imgui_implot(_THIS_DIR + "/../../examples_real_libs/implot/implot.h")


def test_parse_imgui():
    do_parse_imgui_implot(_THIS_DIR + "/../../examples_real_libs/imgui/imgui.h")


def test_parse_code_litgen(code):
    srcml.OPTIONS = srcml.SrmlCppOptions.options_litgen()
    cpp_unit = srcml.parse_code(code)
    print(cpp_unit)


def test_parse_code_preserve(code):
    srcml.OPTIONS = srcml.SrmlCppOptions.options_preserve_code()
    cpp_unit = srcml.parse_code(code)
    print(f">>>{cpp_unit}<<<")


def tree_code(code):
    tree = srcml.code_to_srcml(code, dump_positions=False)
    for child in tree:
        print(child)
    print(srcml.srcml_to_str(tree, bare=True))


def tree_and_parse(code):
    tree_code(code)
    test_parse_code_preserve(code)

# test_parse_implot()
test_parse_imgui()


# test_parse_code_litgen("""
# auto divide(int a, int b) -> double;
# """)

# auto divide(int a, int b) -> double;

