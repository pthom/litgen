from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import Lexer
from pygments.lexers import CppLexer, Python3Lexer
from IPython.core.display import HTML  # type: ignore


HtmlCode = str


def _html_code_viewer(code: str, lexer: Lexer, style: str) -> HtmlCode:
    pygments_css = HtmlFormatter(style=style).get_style_defs(".highlight")
    html_style = f"""<style>{pygments_css}</style>"""

    html_code = highlight(code, lexer, HtmlFormatter())
    html = f"{html_style} {html_code}"
    return html


def html_cpp_code_viewer(code: str) -> HtmlCode:
    lexer = CppLexer()
    # See https://pygments.org/styles/
    style = "gruvbox-light"  # 'solarized-light' #'paraiso-light' #'zenburn' #'solarized-light' # zenburn
    # style = 'solarized-light'
    html = _html_code_viewer(code, lexer, style)
    return html


def html_python_code_viewer(code: str) -> HtmlCode:
    lexer = Python3Lexer()
    style = "gruvbox-light"
    html = _html_code_viewer(code, lexer, style)
    return html


class CodeLanguage(Enum):
    Python = 0
    Cpp = 1


@dataclass
class CodeAndTitle:
    code_language: CodeLanguage
    code: str
    title: str


COLLAPSIBLE_CSS = """
<style>
.collapsible_header {
  background-color: #AAAAAA;
  color: white;
  cursor: pointer;
  padding: 3px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-style: italic;
}

.collapsible_header_opened {
  background-color: #555;
}

.collapsible_header:hover {
  background-color: #AAAAFF;
}

.collapsible_header:after {
  content: '\\002B';
  color: white;
  font-weight: bold;
  float: right;
  margin-left: 5px;
}

.collapsible_header_opened:after {
  content: "\\2212";
}

.collapsible_content {
  padding: 0 18px;
  max-height: 0;
  overflow-x: scroll;
  overflow-y: scroll;
  min-width: 100%;
  transition: max-height 0.2s ease-out;
  background-color: #f1f1f1;
}
</style>
"""


HALF_WIDTH_DIVS_CSS = """
<style>
  div.several_columns {
    display: flex;
    flex-wrap: wrap;
  }
  div.half_width {
     width:49.5%;
     overflow: auto;
  }
  div.half_width_spacer {
     width:1%;
  }
  </style>
"""


_ID_COUNTER = 0


def collapsible_code_and_title(
    code_and_title: CodeAndTitle, max_visible_lines: Optional[int] = None, initially_opened: bool = False
) -> HtmlCode:
    global _ID_COUNTER

    code_as_html: str
    if code_and_title.code_language == CodeLanguage.Python:
        code_as_html = html_python_code_viewer(code_and_title.code)
    else:
        code_as_html = html_cpp_code_viewer(code_and_title.code)

    time_id = str(time.time() * 1000).replace(".", "_")
    collapsible_header_id = "btn_" + time_id + "_" + str(_ID_COUNTER)
    collapsible_content_id = "content_" + time_id + "_" + str(_ID_COUNTER)
    _ID_COUNTER += 1

    copyable_code = code_and_title.code
    copyable_code = copyable_code.replace("`", r"\`").replace("$", r"\$")

    r = COLLAPSIBLE_CSS
    r += f"""
    <script>
       function copy_code_{time_id}() {{
            let code = `{copyable_code}`;
            navigator.clipboard.writeText(code);
       }}
    </script>
    <button class="collapsible_header" id="{collapsible_header_id}" >{code_and_title.title}</button>
    <div class="collapsible_content" id="{collapsible_content_id}">
        <div>
                <button onclick="copy_code_{time_id}()" align="right">copy &#x270d;</button>
        </div>
        {code_as_html}
    </div>
    """

    if max_visible_lines is None:
        max_height_code = 'collapsible_content.scrollHeight + "px"'
    else:
        max_height_code = f'"{max_visible_lines}em"'

    r += f"""
    <script>
    var button = document.getElementById("{collapsible_header_id}");
    button.addEventListener("click", function() {{
        this.classList.toggle("collapsible_header_opened");
        var content = document.getElementById("{collapsible_content_id}");
        if (content.style.maxHeight){{
          content.style.maxHeight = null;
        }} else {{
          content.style.maxHeight = {max_height_code};
        }}
    }});
    </script>
    """

    if initially_opened:
        r += f"""
            <script>
            var collapsible_header = document.getElementById("{collapsible_header_id}");
            collapsible_header.classList.toggle("collapsible_header_opened");
            var collapsible_content = document.getElementById("{collapsible_content_id}");
            collapsible_content.style.maxHeight = {max_height_code};
            </script>
            """

    return r


def collapsible_code_and_title_two_columns(
    code_and_title_1: CodeAndTitle,
    code_and_title_2: CodeAndTitle,
    max_visible_lines: Optional[int] = None,
    initially_opened: bool = False,
) -> HtmlCode:
    viewer_1 = collapsible_code_and_title(
        code_and_title_1, initially_opened=initially_opened, max_visible_lines=max_visible_lines
    )
    viewer_2 = collapsible_code_and_title(
        code_and_title_2, initially_opened=initially_opened, max_visible_lines=max_visible_lines
    )

    html = COLLAPSIBLE_CSS
    html += HALF_WIDTH_DIVS_CSS

    html += f"""
        <div class ="several_columns">
            <div class="half_width">
                {viewer_1}
            </div>
            <div class="half_width_spacer"></div>
            <div class="half_width">
                {viewer_2}
            <br/>
        </div>
    """

    return html


def show_cpp_code(
    code: str, title: str = "", max_visible_lines: Optional[int] = None, initially_opened: bool = True
) -> None:
    from IPython.display import display  # type: ignore

    c = CodeAndTitle(CodeLanguage.Cpp, code, title=title)
    r = collapsible_code_and_title(c, max_visible_lines=max_visible_lines, initially_opened=initially_opened)
    display(HTML(r))  # type: ignore


def show_python_code(
    code: str, title: str = "", max_visible_lines: Optional[int] = None, initially_opened: bool = True
) -> None:
    from IPython.display import display  # type: ignore

    c = CodeAndTitle(CodeLanguage.Python, code, title=title)
    r = collapsible_code_and_title(c, max_visible_lines=max_visible_lines, initially_opened=initially_opened)
    display(HTML(r))  # type: ignore


def show_cpp_file(
    cpp_filename: str, title: str | None = None, max_visible_lines: Optional[int] = None, initially_opened: bool = True
) -> None:
    if title is None:
        title = cpp_filename
    with open(cpp_filename, "r") as f:
        code = f.read()
        show_cpp_code(code, title=title, max_visible_lines=max_visible_lines, initially_opened=initially_opened)


def show_python_file(
    python_filename: str,
    title: str | None = None,
    max_visible_lines: Optional[int] = None,
    initially_opened: bool = True,
) -> None:
    if title is None:
        title = python_filename
    with open(python_filename, "r") as f:
        code = f.read()
        show_python_code(code, title=title, max_visible_lines=max_visible_lines, initially_opened=initially_opened)
