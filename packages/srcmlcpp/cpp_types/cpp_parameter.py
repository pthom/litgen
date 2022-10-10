from dataclasses import dataclass
from typing import List

from srcmlcpp.cpp_types.cpp_decl import CppDecl
from srcmlcpp.cpp_types.cpp_element import (
    CppElement,
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


@dataclass
class CppParameter(CppElementAndComment):
    """
    Most of the time CppParameter is a function parameter.
    However, template parameter are also concerned
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    decl: CppDecl
    template_type: str  # This is only for template's CppParameterList (will be "typename" or "class")
    template_name: str = ""  # This is only for template's CppParameterList (name of the template type, e.g. "T")

    def __init__(self, element: SrcmlWrapper) -> None:
        dummy_cpp_element_comments = CppElementComments()
        super().__init__(element, dummy_cpp_element_comments)

    def type_name_default_for_signature(self) -> str:
        assert hasattr(self, "decl")
        r = self.decl.type_name_default_for_signature()
        return r

    def str_code(self) -> str:
        if hasattr(self, "decl"):
            assert not hasattr(self, "template_type")
            return str(self.decl)
        else:
            if not hasattr(self, "template_type"):
                self.emit_warning("CppParameter.__str__() with no decl and no template_type")
            return str(self.template_type) + " " + self.template_name

    def str_template_type(self) -> str:
        assert hasattr(self, "template_type")
        r = str(self.template_type) + " " + self.template_name
        return r

    def is_template_param(self) -> bool:
        r = hasattr(self, "template_type")
        return r

    def __str__(self) -> str:
        return self.str_code()

    def full_type(self) -> str:
        r = self.decl.cpp_type.str_code()
        return r

    def has_default_value(self) -> bool:
        return len(self.decl.initial_value_code) > 0

    def default_value(self) -> str:
        return self.decl.initial_value_code

    def variable_name(self) -> str:
        return self.decl.decl_name

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)

        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "decl"):
            self.decl.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)


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
