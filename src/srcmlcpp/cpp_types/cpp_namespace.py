from __future__ import annotations
from dataclasses import dataclass

from codemanip import code_utils

from srcmlcpp.cpp_types.base import CppElementAndComment, CppElementsVisitorFunction, CppElementsVisitorEvent
from srcmlcpp.cpp_types.base.cpp_element_comments import CppElementComments
from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppNamespace"]


@dataclass
class CppNamespace(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """

    ns_name: str
    _block: CppBlock

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self.ns_name = ""

    @property
    def block(self) -> CppBlock:
        return self._block

    @block.setter
    def block(self, value: CppBlock) -> None:
        self._block = value
        self.fill_children_parents()

    def str_code(self) -> str:
        r = f"namespace {self.ns_name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), indent_str=self.options.indent_cpp_str)
        r += "}"
        return r

    def __str__(self) -> str:
        return self.str_code()

    def __repr__(self):
        return f"namespace {self.ns_name}"

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "block"):
            self.block.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
