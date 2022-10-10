from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import List, Optional

from srcmlcpp.cpp_types.base import *
from srcmlcpp.cpp_types.blocks import CppBlock, CppPublicProtectedPrivate
from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
from srcmlcpp.cpp_types.decls_types.cpp_type import CppType
from srcmlcpp.cpp_types.functions import CppParameter, CppParameterList
from srcmlcpp.cpp_types.template.icpp_template_host import ICppTemplateHost
from srcmlcpp.cpp_types.template.template_specialization import TemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppFunctionDecl"]


@dataclass
class CppFunctionDecl(CppElementAndComment, ICppTemplateHost):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    specifiers: List[str]  # "const" or ""

    # warning: return_type may include API and inline markers i.e for
    #       MY_API inline int foo()
    # then return_type = "MY_API inline int"
    #
    # Use full_return_type() to get a return type without those.
    return_type: CppType

    parameter_list: CppParameterList
    function_name: str
    is_pure_virtual: bool

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self._init_template_host()
        self.specifiers: List[str] = []
        self.is_pure_virtual = False
        self.function_name = ""

    def qualified_function_name(self) -> str:
        parent_scope = self.cpp_scope(False).str_cpp()
        if len(parent_scope) == 0:
            return self.function_name
        else:
            return parent_scope + "::" + self.function_name

    def qualified_function_name_with_instantiation(self) -> str:
        return self.qualified_function_name() + self.str_template_specialization()

    def function_name_with_instantiation(self) -> str:
        return self.function_name + self.str_template_specialization()

    def with_specialized_template(self, template_specs: TemplateSpecialization) -> Optional[CppFunctionDecl]:
        """Returns a new non-templated function, implemented for the given type
        Only works on templated function with *one* template parameter
        """
        new_function = copy.deepcopy(self)
        new_function._store_template_specs(template_specs)

        was_changed = False

        if hasattr(new_function, "return_type"):
            new_return_type = new_function.return_type.with_specialized_template(template_specs)
            if new_return_type is not None:
                was_changed = True
                new_function.return_type = new_return_type

        new_parameters: List[CppParameter] = []
        for parameter in new_function.parameter_list.parameters:
            new_decl = parameter.decl.with_specialized_template(template_specs)
            if new_decl is not None:
                new_parameter = copy.deepcopy(parameter)
                new_parameter.decl = new_decl
                new_parameters.append(new_parameter)
                was_changed = True
            else:
                new_parameters.append(parameter)

        new_function.parameter_list.parameters = new_parameters

        if was_changed:
            return new_function
        else:
            return None

    def is_inferred_return_type(self) -> bool:
        if not hasattr(self, "return_type"):
            return False
        return "auto" in self.return_type.specifiers and len(self.return_type.typenames) == 0

    def is_arrow_notation_return_type(self) -> bool:
        if self.is_inferred_return_type():
            return False
        elif len(self.return_type.typenames) == 0:
            return False
        else:
            first_typename = self.return_type.typenames[0]
            return first_typename == "auto"

    def _str_signature(self) -> str:
        r = ""

        r += self.str_template()

        if self.is_arrow_notation_return_type():
            if self.return_type.str_return_type() == "auto":
                r += f"auto {self.function_name}{self.str_template_specialization()}({self.parameter_list})"
            else:
                r += f"auto {self.function_name}{self.str_template_specialization()}({self.parameter_list}) -> {self.return_type.str_return_type()}"
        else:
            r += f"{self.return_type.str_return_type()} {self.function_name}{self.str_template_specialization()}({self.parameter_list})"

        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " ".join(specifiers_strs)

        return r

    # def is_auto_decl(self):
    #     self.return_type.typenames[0]

    def str_code(self) -> str:
        r = self._str_signature() + ";"
        return r

    def str_full_return_type(self) -> str:
        """The C++ return type of the function, without API, virtual or inline specifiers"""
        r = self.return_type.str_return_type()
        for prefix in self.options.functions_api_prefixes_list():
            r = r.replace(prefix + " ", "")
        return r

    def is_const(self) -> bool:
        return "const" in self.specifiers

    def is_method(self) -> bool:
        assert hasattr(self, "parent")
        is_method = isinstance(self.parent, CppPublicProtectedPrivate)
        return is_method

    def method_access_type(self) -> str:
        """
        Returns "public", "private", or "protected"
        Will throw if this is not a method!
        """
        assert self.is_method()
        assert hasattr(self, "parent")
        assert isinstance(self.parent, CppPublicProtectedPrivate)
        access_type = self.parent.access_type
        return access_type

    def is_virtual_method(self) -> bool:
        if not self.is_method():
            return False
        if not hasattr(self, "return_type"):
            return False
        is_virtual = "virtual" in self.return_type.specifiers
        return is_virtual

    def is_overloaded_method(self) -> bool:
        if not self.is_method():
            return False
        parent_struct = self.parent_struct_if_method()
        assert parent_struct is not None
        methods_same_name = parent_struct.all_methods_with_name(self.function_name)
        assert len(methods_same_name) >= 1
        is_overloaded = len(methods_same_name) >= 2
        return is_overloaded

    def parent_struct_if_method(self) -> Optional[CppStruct]:
        assert hasattr(self, "parent")
        if not self.is_method():
            return None
        """
        The inner hierarchy of a struct resembles this:
              CppStruct name=MyStruct
                CppBlock scope=MyStruct
                  CppPublicProtectedPrivate scope=MyStruct
                    CppFunctionDecl name=foo scope=MyStruct
                      CppType name=void scope=MyStruct
                      CppParameterList scope=MyStruct
                        ...
        """
        assert self.parent is not None
        assert self.parent.parent is not None
        parent_block = self.parent.parent
        assert isinstance(parent_block, CppBlock)
        parent_struct_ = parent_block.parent
        assert isinstance(parent_struct_, CppStruct)
        return parent_struct_

    def parent_struct_name_if_method(self) -> Optional[str]:
        parent_struct = self.parent_struct_if_method()
        if parent_struct is None:
            return None
        else:
            return parent_struct.class_name

    def is_constructor(self) -> bool:
        parent_struct_name = self.parent_struct_name_if_method()
        if parent_struct_name is None:
            return False
        r = self.function_name == parent_struct_name
        return r

    def is_operator(self) -> bool:
        return self.function_name.startswith("operator")

    def operator_name(self) -> str:
        assert self.is_operator()
        r = self.function_name[len("operator") :]
        return r

    def returns_pointer(self) -> bool:
        r = hasattr(self, "return_type") and self.return_type.modifiers == ["*"]
        return r

    def returns_reference(self) -> bool:
        r = hasattr(self, "return_type") and self.return_type.modifiers == ["&"]
        return r

    def returns_void(self) -> bool:
        return self.str_full_return_type() == "void"

    def is_static(self) -> bool:
        if not hasattr(self, "return_type"):
            return False
        return "static" in self.return_type.specifiers

    def is_static_method(self) -> bool:
        return self.is_method() and self.is_static()

    def __str__(self) -> str:
        return self.str_commented()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "return_type"):
            self.return_type.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        if hasattr(self, "parameter_list"):
            self.parameter_list.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        if hasattr(self, "template"):
            self.template.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
