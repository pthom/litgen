from litgen.demo.code_notebook_display import display_cpp_python_code
from litgen import GeneratedCodes, LitgenOptions
import litgen


def display_generated_code(generate_codes: GeneratedCodes) -> None:
    display_cpp_python_code(generate_codes.pydef_code, generate_codes.stub_code)


def generate_and_display(options: LitgenOptions, code: str) -> None:
    generated_codes = litgen.generate_code(options, code, omit_boxed_types_code=True)
    display_generated_code(generated_codes)
