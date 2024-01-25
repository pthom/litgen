from __future__ import annotations
from IPython.core.display import HTML  # type: ignore

from codemanip.html_code_viewer.html_code_viewer import (
    CodeAndTitle,
    CodeLanguage,
    collapsible_code_and_title,
    collapsible_code_and_title_two_columns,
    show_cpp_code as show_cpp_code,  # noqa
    show_python_code as show_python_code,  # noqa
    show_cpp_file as show_cpp_file,  # noqa
    show_python_file as show_python_file,  # noqa
)

import litgen
from litgen import LitgenOptions


def _generate_and_display_impl(
    options: LitgenOptions, cpp_code: str, display_original_cpp_code: bool, collapse_pydef: bool, max_visible_lines: int
) -> str:
    generated_codes = litgen.generate_code(options, cpp_code)

    original_content = CodeAndTitle(CodeLanguage.Cpp, cpp_code, "Original C++ decls")
    stubs_content = CodeAndTitle(CodeLanguage.Python, generated_codes.stub_code, "Corresponding python decls (stub)")
    pydef_content = CodeAndTitle(CodeLanguage.Cpp, generated_codes.pydef_code, "pybind11 C++ binding code")
    glue_code = CodeAndTitle(CodeLanguage.Cpp, generated_codes.glue_code, "C++ glue code")

    initially_open_cpp_code = not collapse_pydef
    collapsible_pydef = collapsible_code_and_title(
        pydef_content, max_visible_lines=max_visible_lines, initially_opened=initially_open_cpp_code
    )
    collapsible_glue_code = collapsible_code_and_title(
        glue_code, max_visible_lines=max_visible_lines, initially_opened=initially_open_cpp_code
    )

    if display_original_cpp_code:
        html = collapsible_code_and_title_two_columns(
            original_content, stubs_content, initially_opened=True, max_visible_lines=max_visible_lines
        )
    else:
        html = collapsible_code_and_title(stubs_content, initially_opened=True, max_visible_lines=max_visible_lines)

    html += f"<br/>{collapsible_pydef}"

    if len(generated_codes.glue_code) > 0:
        html += f"<br/>{collapsible_glue_code}"

    return html


def demo(
    options: LitgenOptions,
    cpp_code: str,
    show_cpp: bool = True,
    show_pydef: bool = False,
    height: int = 40,
) -> None:
    from IPython.display import display  # type: ignore

    collapse_pydef = not show_pydef
    html = _generate_and_display_impl(options, cpp_code, show_cpp, collapse_pydef, height)
    display(HTML(html))  # type: ignore
