from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import List, Optional

from codemanip import code_utils

from srcmlcpp.cpp_types.base import *
from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl
from srcmlcpp.cpp_types.template.template_specialization import TemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppDeclStatement"]


@dataclass
class CppDeclStatement(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """

    cpp_decls: List[CppDecl]  # A CppDeclStatement can initialize several variables

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self.cpp_decls: List[CppDecl] = []

    def str_code(self) -> str:
        str_decls = list(
            map(
                lambda cpp_decl: cpp_decl.str_commented(is_decl_stmt=True),
                self.cpp_decls,
            )
        )
        str_decl = code_utils.join_remove_empty("\n", str_decls)
        return str_decl

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        for child in self.cpp_decls:
            child.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def with_specialized_template(self, template_specs: TemplateSpecialization) -> Optional[CppDeclStatement]:
        """Returns a new CppDeclStatement where "template_name" is replaced by "cpp_type"
        Returns None if this CppDeclStatement does not use "template_name"
        """
        was_changed = False

        new_decl_statement = copy.deepcopy(self)
        new_cpp_decls: List[CppDecl] = []
        for cpp_decl in new_decl_statement.cpp_decls:
            new_cpp_decl = cpp_decl.with_specialized_template(template_specs)
            if new_cpp_decl is not None:
                was_changed = True
                new_cpp_decls.append(new_cpp_decl)
            else:
                new_cpp_decls.append(cpp_decl)

        if not was_changed:
            return None
        else:
            new_decl_statement.cpp_decls = new_cpp_decls
            return new_decl_statement

    def __str__(self) -> str:
        return self.str_commented()
