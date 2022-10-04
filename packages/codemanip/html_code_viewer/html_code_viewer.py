from typing import Optional

from dataclasses import dataclass
from enum import Enum
import time

from pygments import highlight
from pygments.lexers import Python3Lexer, CppLexer
from pygments.lexer import Lexer
from pygments.formatters import HtmlFormatter


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
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 10px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.collapsible:after {
  content: '\\002B';
  color: white;
  font-weight: bold;
  float: right;
  margin-left: 5px;
}

.active:after {
  content: "\\2212";
}

.content {
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

# overflow: auto;
# overflow-wrap: normal;


HALF_WIDTH_DIVS_CSS = """
<style>
  div.several_columns {
    display: flex;
    flex-wrap: wrap;
  }
  div.half_width {
     width:48.5%;
     overflow: auto;
  }
  div.half_width_spacer {
     width:3%;
  }
  </style>
"""


def collapsible_code_and_title(
    code_and_title: CodeAndTitle, max_visible_lines: Optional[int] = None, initially_opened: bool = False
) -> HtmlCode:
    # r = COLLAPSIBLE_CSS

    code_as_html = ""
    if code_and_title.code_language == CodeLanguage.Python:
        code_as_html = html_python_code_viewer(code_and_title.code)
    else:
        code_as_html = html_cpp_code_viewer(code_and_title.code)

    time_id = str(time.time() * 1000).replace(".", "_")
    button_id = "btn_" + time_id
    content_id = "content_" + time_id

    r = ""
    r += f"""
    <button class="collapsible" id="{button_id}" >{code_and_title.title}</button>
    <div class="content" id="{content_id}">
    {code_as_html}
    </div>
    """

    if max_visible_lines is None:
        max_height_code = 'content.scrollHeight + "px"'
    else:
        max_height_code = f'"{max_visible_lines}em"'

    r += f"""
    <script>
    var button = document.getElementById("{button_id}");
    button.addEventListener("click", function() {{
        this.classList.toggle("active");
        var content = document.getElementById("{content_id}");
        //var content = this.nextElementSibling;
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
            var content = document.getElementById("{content_id}");
            content.style.maxHeight = {max_height_code};
            </script>
            """

    return r
