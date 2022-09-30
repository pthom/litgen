from dataclasses import dataclass
from typing import List

from pygments import highlight
from pygments.lexers import Python3Lexer, CppLexer
from pygments.lexer import Lexer
from pygments.formatters import HtmlFormatter

# from pygments.styles import get_style_by_name

from IPython.core.display import HTML  # type: ignore


HtmlCode = str


def display_wrapper(html_code: HtmlCode) -> None:
    display(HTML(html_code))  # type: ignore


def html_display_code(code: str, lexer: Lexer, style: str) -> HtmlCode:
    pygments_css = HtmlFormatter(style=style).get_style_defs(".highlight")
    html_style = f"""<style>{pygments_css}</style>"""

    html_code = highlight(code, lexer, HtmlFormatter())
    html = f"{html_style} {html_code}"
    return html


def html_cpp_code(code: str) -> HtmlCode:
    lexer = CppLexer()
    # See https://pygments.org/styles/
    style = "gruvbox-light"  # 'solarized-light' #'paraiso-light' #'zenburn' #'solarized-light' # zenburn
    # style = 'solarized-light'
    html = html_display_code(code, lexer, style)
    return html


def html_python_code(code: str) -> HtmlCode:
    lexer = Python3Lexer()
    style = "gruvbox-light"
    html = html_display_code(code, lexer, style)
    return html


def display_cpp_code(code: str) -> None:
    display_wrapper(html_cpp_code(code))


def display_python_code(code: str) -> None:
    display_wrapper(html_python_code(code))


@dataclass
class CodeAndTitle:
    code: str
    title: str


def display_cpp_python_code(cpp_code: str, python_code: str) -> None:
    html_cpp = html_cpp_code(cpp_code)
    html_python = html_python_code(python_code)
    c1 = CodeAndTitle(html_python, "Python stub (declarations)")
    c2 = CodeAndTitle(html_cpp, "C++ Pydef code")
    display_several_codes([c1, c2])


def display_several_codes(codes: List[CodeAndTitle]) -> None:
    assert len(codes) == 2
    c1 = codes[0]
    c2 = codes[1]
    html_table = f"""
    <table>
        <tr>
            <td align="left" bgcolor="#eeee55"><div align="left">{c1.title}</div></td>
            <td width="10px"></td>
            <td align="left" bgcolor="#99ee99"><div align="left">{c2.title}</div></td>
        </tr>
        <tr>
            <td align="left"><div align="left">{c1.code}</div></td>
            <td width="10px"></td>
            <td align="left"><div align="left">{c2.code}</div></td>
        </tr>
    </table>
    """
    display_wrapper(html_table)
