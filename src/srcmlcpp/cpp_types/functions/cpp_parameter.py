from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.scrml_warning_settings import WarningType
from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppParameter"]


@dataclass
class CppParameter(CppElementAndComment):
    """
    Most of the time CppParameter is a function parameter.
    However, template parameter are also concerned
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    _decl: CppDecl

    template_type: str  # This is only for template's CppParameterList (will be "typename" or "class")
    template_name: str = ""  # This is only for template's CppParameterList (name of the template type, e.g. "T")
    template_init: str = ""  # For templates with default int value, e.g. `template<int N=1> void f()`

    def __init__(self, element: SrcmlWrapper) -> None:
        dummy_cpp_element_comments = CppElementComments()
        super().__init__(element, dummy_cpp_element_comments)

    @property
    def decl(self) -> CppDecl:
        return self._decl

    @decl.setter
    def decl(self, new_decl: CppDecl) -> None:
        self._decl = new_decl
        self._decl.parent = self

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
                self.emit_warning("CppParameter.__str__() with no decl and no template_type", WarningType.Unclassified)
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

    def __repr__(self):
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
