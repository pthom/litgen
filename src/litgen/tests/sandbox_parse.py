from __future__ import annotations
import os
import sys

import litgen
from litgen import LitgenOptions
from litgen.litgen_generator import LitgenGeneratorTestsHelper


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def read_file_content(filename: str) -> str:
    with open(filename) as f:
        content = f.read()
    return content


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
    options = litgen.LitgenOptions()
    # options.srcmlcpp_options.fix_brace_init_default_value = False

    code = """
    struct TobiiResearchPoint3D
    {
        float x;
        float y;
        float z;
    };
    struct gazeOrigin
    {
        // The gaze origin position in 3D in the user coordinate system.
        TobiiResearchPoint3D position_in_user_coordinates = {1.f, 2.f, 3.f};

        bool available = false;
    };
        """

    # code = "void f(V v={1,2,3});"

    # options = litgen_options_imgui(ImguiOptionsType.imgui_h, True)
    # options.fn_template_options.add_specialization(".*", ["int"])
    # options.class_deep_copy__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    print(generated_code.stub_code)


if __name__ == "__main__":
    play()
