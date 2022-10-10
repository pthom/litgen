from dataclasses import dataclass
from typing import List

from srcmlcpp.cpp_types.base import *
from srcmlcpp.cpp_types.functions.cpp_parameter import CppParameter
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppParameterList"]


@dataclass
class CppParameterList(CppElement):
    """
    List of parameters of a function (or list of template parameters)
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    parameters: List[CppParameter]

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element)
        self.parameters = []

    def list_types_names_only(self) -> List[str]:
        """Returns a list like ["int", "bool"]"""
        r = []
        for parameter in self.parameters:
            r.append(parameter.decl.cpp_type.str_code())
        return r

    def str_types_names_only(self) -> str:
        return ", ".join(self.list_types_names_only())

    def list_types_names_default_for_signature(self) -> List[str]:
        """Returns a list like ["int a", "bool flag = true"]"""
        params_strs = list(map(lambda param: param.type_name_default_for_signature(), self.parameters))
        return params_strs

    def str_types_names_default_for_signature(self) -> str:
        """Returns a string like "int a, bool flag = true" """
        params_strs = self.list_types_names_default_for_signature()
        params_str = ", ".join(params_strs)
        return params_str

    def str_code(self) -> str:
        return self.str_types_names_default_for_signature()

    def str_names_only_for_call(self) -> str:
        names = [param.variable_name() for param in self.parameters]
        r = ", ".join(names)
        return r

    def str_types_only_for_overload(self) -> str:
        def type_with_star_for_array(param: CppParameter) -> str:
            type_str = param.decl.cpp_type.str_code()
            if param.decl.c_array_code.startswith("["):
                type_str += " *"
            return type_str

        types = [type_with_star_for_array(param) for param in self.parameters]
        r = ", ".join(types)
        return r

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        for child in self.parameters:
            child.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def __str__(self) -> str:
        return self.str_code()
