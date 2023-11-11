from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
    CppElementComments,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.functions import CppParameterList


__all__ = ["CppTemplate"]


@dataclass
class CppTemplate(CppElementAndComment):
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """

    _parameter_list: CppParameterList

    def __init__(self, element: SrcmlWrapper) -> None:
        from srcmlcpp.cpp_types.functions.cpp_parameter_list import CppParameterList

        empty_comments = CppElementComments()
        super().__init__(element, empty_comments)
        self._parameter_list = CppParameterList(element)

    @property
    def parameter_list(self) -> CppParameterList:
        return self._parameter_list

    @parameter_list.setter
    def parameter_list(self, value: CppParameterList) -> None:
        self._parameter_list = value
        self.fill_children_parents()

    def str_code(self) -> str:
        typelist = [param.str_template_type() for param in self.parameter_list.parameters]
        typelist_str = ", ".join(typelist)
        params_str = f"template<{typelist_str}> "
        return params_str

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "parameter_list"):
            self.parameter_list.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def __str__(self) -> str:
        return self.str_code()
