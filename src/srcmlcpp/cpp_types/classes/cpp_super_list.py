from __future__ import annotations
from dataclasses import dataclass

from codemanip import code_utils

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementsVisitorFunction,
    CppElementsVisitorEvent,
    CppElementComments,
)
from srcmlcpp.cpp_types.classes.cpp_super import CppSuper
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppSuperList"]


@dataclass
class CppSuperList(CppElementAndComment):
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    _super_list: list[CppSuper]

    def __init__(self, element: SrcmlWrapper):
        empty_comments = CppElementComments()
        super().__init__(element, empty_comments)
        self._super_list: list[CppSuper] = []

    @property
    def super_list(self) -> list[CppSuper]:
        return self._super_list

    @super_list.setter
    def super_list(self, value: list[CppSuper]) -> None:
        self._super_list = value
        self.fill_children_parents()

    def str_code(self) -> str:
        strs = list(map(str, self.super_list))
        return " : " + code_utils.join_remove_empty(", ", strs)

    def __str__(self) -> str:
        return self.str_code()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        for super_class in self.super_list:
            super_class.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
