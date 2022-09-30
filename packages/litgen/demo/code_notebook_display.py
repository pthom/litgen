from dataclasses import dataclass
from typing import List
from enum import Enum

from pygments import highlight
from pygments.lexers import Python3Lexer, CppLexer
from pygments.lexer import Lexer
from pygments.formatters import HtmlFormatter

# from pygments.styles import get_style_by_name

from IPython.core.display import HTML  # type: ignore


HtmlCode = str


def display_wrapper(html_code: HtmlCode) -> None:
    display(HTML(html_code))  # type: ignore


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


def display_cpp_code(code: str) -> None:
    display_wrapper(html_cpp_code_viewer(code))


def display_python_code(code: str) -> None:
    display_wrapper(html_python_code_viewer(code))


class CodeLanguage(Enum):
    Python = 0
    Cpp = 1


@dataclass
class CodeAndTitle:
    code_language: CodeLanguage
    code: str
    title: str


def display_several_codes(codes: List[CodeAndTitle]) -> None:

    c1 = codes[0]
    c2 = codes[1]
    c3 = codes[2]

    # lines1 = c1.code.count("\n")
    # lines2 = c2.code.count("\n")
    # nb_lines = max(lines1, lines2) # Marche pas!!!
    nb_lines = 12

    html = f"""
    <style>
      div.several_codes {{
        display: flex;
        flex-wrap: wrap;
        justify-content: space-evenly;
      }}
      div.scroll_title_half {{
        height: {nb_lines + 1}em;
        flex-basis: 47%;
      }}
      div.scroll_title_full {{
        width: 95%;
        height: {nb_lines + 1}em;
      }}
      div.scrollable_code_viewer {{
        width: 100%;
        height: {nb_lines}em;
        overflow: auto;
        background-color: #f9f1cb
      }}
    </style>
    """

    html += f"""
    <div class ="several_codes">
        <div class="scroll_title_half">
            {c1.title}
            <div class="scrollable_code_viewer">{c1.code}</div>
        </div>
        <div class="scroll_title_half">
            {c2.title}
            <div class="scrollable_code_viewer">{c2.code}</div>
        </div>
        <div class="scroll_title_full">
            <br/>
            {c3.title}
            <div class="scrollable_code_viewer">{c3.code}</div>
        </div>
    </div>
    """
    display_wrapper(html)
