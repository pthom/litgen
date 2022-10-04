from litgen import LitgenOptions
import litgen

from IPython.core.display import HTML  # type: ignore


from codemanip.html_code_viewer.html_code_viewer import (
    CodeLanguage,
    CodeAndTitle,
    collapsible_code_and_title,
    COLLAPSIBLE_CSS,
    HALF_WIDTH_DIVS_CSS,
)


def generate_and_display_impl(options: LitgenOptions, cpp_code: str) -> str:
    generated_codes = litgen.generate_code(options, cpp_code, omit_boxed_types_code=True)

    original_content = CodeAndTitle(CodeLanguage.Cpp, cpp_code, "Original C++ decls")
    stubs_content = CodeAndTitle(CodeLanguage.Python, generated_codes.stub_code, "Corresponding python decls (stub)")
    pydef_content = CodeAndTitle(CodeLanguage.Cpp, generated_codes.pydef_code, "pybind11 C++ binding code")
    boxed_types_content = CodeAndTitle(CodeLanguage.Cpp, generated_codes.boxed_types_cpp_code, "C++ boxed types")

    original_viewer = collapsible_code_and_title(original_content, initially_opened=True)
    stubs_viewer = collapsible_code_and_title(stubs_content, initially_opened=True)
    pydef_viewer = collapsible_code_and_title(pydef_content, max_visible_lines=20)
    boxed_types_viewer = collapsible_code_and_title(boxed_types_content)

    html = COLLAPSIBLE_CSS
    html += HALF_WIDTH_DIVS_CSS

    html += f"""
        <div class ="several_columns">
            <div class="half_width">
                {original_viewer}
            </div>
            <div class="half_width_spacer"></div>
            <div class="half_width">
                {stubs_viewer}
            <br/>
        </div>
        <br/>
        {pydef_viewer}
        <br/>
        {boxed_types_viewer}
    """
    return html


def generate_and_display(options: LitgenOptions, cpp_code: str) -> None:
    from IPython.display import display  # type: ignore

    html = generate_and_display_impl(options, cpp_code)
    display(HTML(html))
