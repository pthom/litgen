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
    options.globals_vars_include_by_name__regex = r"^PI_|white|red"
    # options.globals_vars_include_by_name__regex = r".*"

    code = """
    static float PI_2 = 6.283185307179586f;
    void foo()
    {
        circle([&] (int i) {
                    const float a = PI_2 * i / num_segments;
                    const float x = (scale(16) * ImPow(ImSin(a), 3));
                    const float y = -1.f * (scale(13) * ImCos(a) - scale(5) * ImCos(2 * a) - scale(2) * ImCos(3 * a) - ImCos(4 * a));
                    return rotate(ImVec2(x, y), ang_min);
                }, color_alpha(color, 1.f), thickness);
    }
        """
    generated_code = litgen.generate_code(options, code)
    print(generated_code.stub_code)

    print(generated_code.pydef_code)


if __name__ == "__main__":
    play()
