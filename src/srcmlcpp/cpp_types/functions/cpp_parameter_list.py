from __future__ import annotations
from dataclasses import dataclass
import copy

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope
from srcmlcpp.cpp_types.functions.cpp_parameter import CppParameter
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppParameterList"]


@dataclass
class CppParameterList(CppElementAndComment):
    """
    List of parameters of a function (or list of template parameters)
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    _parameters: list[CppParameter]

    def __init__(self, element: SrcmlWrapper) -> None:
        empty_comments = CppElementComments()
        super().__init__(element, empty_comments)
        self._parameters = []

    @property
    def parameters(self) -> list[CppParameter]:
        return self._parameters

    @parameters.setter
    def parameters(self, new_parameters: list[CppParameter]) -> None:
        self._parameters = new_parameters
        self.fill_children_parents()

    def list_types_names_only(self) -> list[str]:
        """Returns a list like ["int", "bool"]"""
        r = []
        for parameter in self.parameters:
            r.append(parameter.decl.cpp_type.str_code())
        return r

    def str_types_names_only(self) -> str:
        return ", ".join(self.list_types_names_only())

    def contains_pointer_to_pointer_param(self) -> bool:
        for p in self.parameters:
            if p.decl.cpp_type.modifiers.count("*") == 2:
                return True
        return False

    def list_types_names_default_for_signature(self) -> list[str]:
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

    def with_qualified_types(self, current_scope: CppScope | None = None) -> CppParameterList:
        """Returns a possibly new FunctionDecl where the params and return types are qualified given the function scope.

        For example, given the code:
            namespace Ns {
                struct S {};
                void f(S s);
            }
        then, f.with_qualified_types = void f(Ns::S s)
        """
        if current_scope is None:
            current_scope = self.cpp_scope()
        was_changed = False
        # new_parameter_list = copy.deepcopy(self)
        new_parameters: list[CppParameter] = []

        # handle void instead of empty param:
        #     void foo(void)
        if len(self.parameters) == 1 and self.parameters[0].decl.cpp_type.is_void():
            new_parameters = []
            was_changed = True
        else:
            for i in range(len(self.parameters)):
                # new_param = new_parameter_list.parameters[i]
                self_param = self.parameters[i]
                new_param_decl = self_param.decl.with_qualified_types(current_scope)
                if new_param_decl is not self_param.decl:
                    new_param = copy.deepcopy(self.parameters[i])
                    new_param.decl = new_param_decl
                    new_parameters.append(new_param)
                    was_changed = True
                else:
                    new_parameters.append(self_param)

        if was_changed:
            r = copy.deepcopy(self)
            r.parameters = new_parameters
            return r
        else:
            return self

    def with_terse_types(self, current_scope: CppScope | None = None) -> CppParameterList:
        if current_scope is None:
            current_scope = self.cpp_scope()
        was_changed = False
        # new_parameter_list = copy.deepcopy(self)
        new_parameters: list[CppParameter] = []
        for i in range(len(self.parameters)):
            self_param = self.parameters[i]
            new_decl = self_param.decl.with_terse_types(current_scope)
            if new_decl is not self_param.decl:
                was_changed = True
                new_parameter = copy.deepcopy(self_param)
                new_parameter.decl = new_decl
                new_parameters.append(new_parameter)
            else:
                new_parameters.append(self_param)

        if was_changed:
            new_parameter_list = copy.deepcopy(self)
            new_parameter_list.parameters = new_parameters
            return new_parameter_list
        else:
            return self

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        for child in self.parameters:
            child.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def __str__(self) -> str:
        return self.str_code()
