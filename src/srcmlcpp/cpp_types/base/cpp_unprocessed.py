from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import CppElementAndComment, CppElementComments
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppEmptyLine", "CppUnprocessed", "CppComment"]


@dataclass
class CppEmptyLine(CppElementAndComment):
    """Describe an empty line. This is not part of srcML, and was added in srcmlcpp
    in order to better keep track of function and classes comments.
    """

    def __init__(self, element: SrcmlWrapper) -> None:
        dummy_comments = CppElementComments()
        super().__init__(element, dummy_comments)

    def str_code(self) -> str:
        return ""

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False) -> str:
        return ""

    def __str__(self) -> str:
        return ""

    def __repr__(self):
        return "<empty_line>"


class CppUnprocessed(CppElementAndComment):
    """Any Cpp Element that is not yet processed by srcmlcpp
    The original source can be accessed via self.str_code_verbatim()
    """

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self.code = ""

    def str_code(self) -> str:
        return f"<unprocessed_{self.tag()}/>"

    def __str__(self) -> str:
        self.str_code_verbatim()
        return self.str_commented()


@dataclass
class CppComment(CppElementAndComment):
    """https://www.srcml.org/doc/cpp_srcML.html#comment
    Warning, the text contains "//" or "/* ... */" and "\n"
    """

    comment: str

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    def str_code(self) -> str:
        lines = self.comment.split("\n")  # split("\n") keeps empty lines (splitlines() does not!)
        lines = list(map(lambda s: "// " + s, lines))
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.str_code()
