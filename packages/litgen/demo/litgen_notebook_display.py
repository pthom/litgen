from litgen import LitgenOptions
import litgen

from IPython.core.display import HTML  # type: ignore


from codemanip.html_code_viewer.html_code_viewer import (
    CodeLanguage,
    CodeAndTitle,
    collapsible_code_and_title,
    collapsible_code_and_title_two_columns,
)


def generate_and_display_impl(options: LitgenOptions, cpp_code: str) -> str:
    generated_codes = litgen.generate_code(options, cpp_code)

    original_content = CodeAndTitle(CodeLanguage.Cpp, cpp_code, "Original C++ decls")
    stubs_content = CodeAndTitle(CodeLanguage.Python, generated_codes.stub_code, "Corresponding python decls (stub)")
    pydef_content = CodeAndTitle(CodeLanguage.Cpp, generated_codes.pydef_code, "pybind11 C++ binding code")
    boxed_types_content = CodeAndTitle(CodeLanguage.Cpp, generated_codes.boxed_types_cpp_code, "C++ boxed types")

    collapsible_pydef = collapsible_code_and_title(pydef_content, max_visible_lines=20)
    collapsible_boxed_types = collapsible_code_and_title(boxed_types_content)

    html = collapsible_code_and_title_two_columns(original_content, stubs_content, initially_opened=True)

    html += f"<br/>{collapsible_pydef}"

    if len(generated_codes.boxed_types_cpp_code) > 0:
        html += f"<br/>{collapsible_boxed_types}"

    return html


def generate_and_display(options: LitgenOptions, cpp_code: str) -> None:
    from IPython.display import display  # type: ignore

    html = generate_and_display_impl(options, cpp_code)
    display(HTML(html))
