from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base.cpp_element import CppElement
from srcmlcpp.cpp_types.base.cpp_element_comments import CppElementComments
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppElementAndComment"]


@dataclass
class CppElementAndComment(CppElement):
    """A CppElement to which we add comments"""

    cpp_element_comments: CppElementComments

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element)
        self.cpp_element_comments = cpp_element_comments

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False) -> str:
        result = self.cpp_element_comments.top_comment_code()
        result += self.str_code()
        if is_enum:
            result += ","
        if is_decl_stmt:
            result += ";"
        result += self.cpp_element_comments.eol_comment_code()
        return result

    def __str__(self) -> str:
        return self.str_commented()

    def __repr__(self):
        return f"CppElementAndComment({self.str_commented()})"
