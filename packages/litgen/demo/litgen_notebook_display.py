from typing import List

from litgen.demo.code_notebook_display import (
    display_several_codes,
    html_cpp_code_viewer,
    html_python_code_viewer,
    CodeLanguage,
    CodeAndTitle,
)
from litgen import LitgenOptions
import litgen


def generate_and_display(options: LitgenOptions, cpp_code: str) -> None:
    generated_codes = litgen.generate_code(options, cpp_code, omit_boxed_types_code=True)

    codes: List[CodeAndTitle] = []

    codes.append(CodeAndTitle(CodeLanguage.Cpp, html_cpp_code_viewer(cpp_code), "Original C++ decls"))
    codes.append(
        CodeAndTitle(
            CodeLanguage.Python, html_python_code_viewer(generated_codes.stub_code), "Corresponding python decls (stub)"
        )
    )
    codes.append(
        CodeAndTitle(CodeLanguage.Cpp, html_cpp_code_viewer(generated_codes.pydef_code), "pybind11 C++ binding code")
    )
    if len(generated_codes.boxed_types_cpp_code) > 0:
        codes.append(
            CodeAndTitle(
                CodeLanguage.Cpp, html_cpp_code_viewer(generated_codes.boxed_types_cpp_code), "C++ boxed types"
            )
        )

    display_several_codes(codes)
