from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import CppElementComments, CppElementsVisitorFunction, CppElementsVisitorEvent
from srcmlcpp.cpp_types.base.cpp_unprocessed import CppUnprocessed
from srcmlcpp.cpp_types.functions.cpp_function_decl import CppFunctionDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppFunction"]


@dataclass
class CppFunction(CppFunctionDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """

    _block: CppUnprocessed

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    @property
    def block(self) -> CppUnprocessed:
        return self._block

    @block.setter
    def block(self, value: CppUnprocessed) -> None:
        self._block = value
        self.fill_children_parents()

    def str_code(self) -> str:
        r = self._str_signature()
        if hasattr(self, "block"):
            r += str(self.block)
        return r

    def __str__(self) -> str:
        r = ""
        if len(self.cpp_element_comments.top_comment_code()) > 0:
            r += self.cpp_element_comments.top_comment_code()
        r += self._str_signature() + self.cpp_element_comments.eol_comment_code()
        r += "\n" + str(self.block) + "\n"
        return r

    def __repr__(self):
        return self._str_signature()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        if hasattr(self, "block"):
            cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
            self.block.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
            cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
