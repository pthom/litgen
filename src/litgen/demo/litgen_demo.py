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
    options: LitgenOptions, cpp_code: str, show_cpp: bool, show_pydef: bool, height: int
) -> str:
    # First generate the code for pybind11
    options.bind_library = litgen.BindLibraryType.pybind11
    generated_codes = litgen.generate_code(options, cpp_code)

    original_content = CodeAndTitle(CodeLanguage.Cpp, cpp_code, "Original C++ decls")
    stubs_content = CodeAndTitle(CodeLanguage.Python, generated_codes.stub_code, "Corresponding python decls (stub)")
    glue_code = CodeAndTitle(CodeLanguage.Cpp, generated_codes.glue_code, "C++ glue code")
    pydef_pybind = CodeAndTitle(CodeLanguage.Cpp, generated_codes.pydef_code, "pybind11 C++ binding code")

    # Then generate the code for nanobind (only the binding code)
    options.bind_library = litgen.BindLibraryType.nanobind
    generated_codes_nano = litgen.generate_code(options, cpp_code)
    pydef_nanobind = CodeAndTitle(CodeLanguage.Cpp, generated_codes_nano.pydef_code, "nanobind C++ binding code")

    if show_cpp:
        html = collapsible_code_and_title_two_columns(
            original_content, stubs_content, initially_opened=True, max_visible_lines=height
        )
    else:
        html = collapsible_code_and_title(stubs_content, initially_opened=True, max_visible_lines=height)

    collapsible_pydef = collapsible_code_and_title(
        pydef_pybind, max_visible_lines=height, initially_opened=show_pydef
    ) + collapsible_code_and_title(pydef_nanobind, max_visible_lines=height, initially_opened=show_pydef)
    html += f"<br/>{collapsible_pydef}"

    if len(generated_codes.glue_code) > 0:
        collapsible_glue_code = collapsible_code_and_title(
            glue_code, max_visible_lines=height, initially_opened=show_pydef
        )
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

    html = _generate_and_display_impl(options, cpp_code, show_cpp, show_pydef, height)
    display(HTML(html))  # type: ignore
