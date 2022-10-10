from dataclasses import dataclass

from codemanip import code_utils

from srcmlcpp.cpp_types.cpp_blocks import CppBlock
from srcmlcpp.cpp_types.cpp_element import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


@dataclass
class CppNamespace(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """

    ns_name: str
    block: CppBlock

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self.ns_name = ""

    def str_code(self) -> str:
        r = f"namespace {self.ns_name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), indent_str=self.options.indent_cpp_str)
        r += "}"
        return r

    def __str__(self) -> str:
        return self.str_code()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "block"):
            self.block.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
