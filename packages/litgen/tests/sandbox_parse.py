import os
import sys

import srcmlcpp

import litgen
from litgen import LitgenOptions
from litgen.litgen_generator import LitgenGeneratorTestsHelper
from litgen.options_customized.litgen_options_imgui import litgen_options_imgui
from litgen.options_customized.litgen_options_implot import litgen_options_implot


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def read_file_content(filename: str) -> str:
    with open(filename, "r") as f:
        content = f.read()
    return content


def play_parse(code: str) -> None:
    options = litgen_options_imgui()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcmlcpp_options, code)
    print(cpp_unit)


def play_stub(code: str, options: LitgenOptions) -> None:
    pyi_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    print(f">>>\n{pyi_code}<<<")


def play_pydef(code: str, options: LitgenOptions) -> None:
    pyi_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    print(f">>>\n{pyi_code}<<<")


def litgensample_options() -> litgen.LitgenOptions:
    options = litgen.LitgenOptions()
    options.fn_params_replace_c_array_modifiable_by_boxed__regex = "array"
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    return options


def my_play() -> None:
    code = """
//IMPLOT_API void truc(float* a = NULL, float* b = NULL);
IMPLOT_API std::tuple<std::vector<int>, std::vector<float>> foo();
    """
    options = litgen_options_implot()
    generated_code = litgen.generate_code(options, code)
    print(generated_code.stub_code)


def play_operator() -> None:
    code = """
struct IntWrapper
{
    int value;

    IntWrapper operator<=>(IntWrapper b) { return IntWrapper{ value - b.value}; }
};
    """
    options = LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    print(generated_code.stub_code)


def play_private_destructor() -> None:
    code = """
class Foo
{
    ~Foo();
};
    """
    options = LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    print(generated_code.pydef_code)


def play_virtual_method() -> None:
    # See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions
    code = """
    struct Base
    {
        int a = 0
    };
    struct Derivate: public Base
    {
        int b;
    };
    """
    options = LitgenOptions()
    # options.fn_params_replace_modifiable_immutable_by_boxed__regex  = ".*"
    options.class_expose_protected_methods__regex = ".*"
    options.class_override_virtual_methods_in_python__regex = ".*"
    generated_code = litgen.generate_code(options, code)
    print(generated_code.pydef_code)


def play() -> None:
    code = """
struct ImColor
{
    inline operator ImVec4() const;
};
    """
    options = litgen.LitgenOptions()
    options.fn_template_options.add_specialization(r"SumVector", ["int"])
    options.fn_params_replace_buffer_by_array__regex = r".*"
    # options.srcmlcpp_options.functions_api_prefixes = "MY_API"

    # generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    # print(generated_code.stub_code)

    # srcmlcpp_options = srcmlcpp.SrcmlcppOptions()
    # srcmlcpp_options.flag_srcml_dump_positions = False
    # xml_wrapper = srcmlcpp.code_to_srcml_wrapper(srcmlcpp_options, code)
    # print(xml_wrapper.str_xml())

    srcmlcpp_options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(srcmlcpp_options, code)
    f = cpp_unit.all_functions_recursive()[0]
    print(f)
    # f = cpp_unit.all_functions_recursive()[0]
    # print(f.str_code())


def play_srcml() -> None:
    code = "int a = 1;"
    options = srcmlcpp.SrcmlcppOptions()
    wrapper = srcmlcpp.code_to_srcml_wrapper(options, code)
    print(wrapper.str_xml())
    print("a")


if __name__ == "__main__":
    # play_srcml()
    play()
