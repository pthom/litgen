from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from srcmlcpp.cpp_types.base import *
from srcmlcpp.cpp_types.cpp_scope import CppScope
from srcmlcpp.cpp_types.decls_types.cpp_type import CppType
from srcmlcpp.cpp_types.functions import CppParameter, CppParameterList
from srcmlcpp.cpp_types.template.cpp_i_template_host import CppITemplateHost
from srcmlcpp.cpp_types.template.cpp_template_specialization import CppTemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct


__all__ = ["CppFunctionDecl"]


@dataclass
class CppFunctionDecl(CppElementAndComment, CppITemplateHost):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    specifiers: List[str]  # can contain "const", "delete" or "default" for constructors & destructors

    # warning: return_type may include API and inline markers i.e for
    #       MY_API inline int foo()
    # then return_type = "MY_API inline int"
    #
    # Use full_return_type() to get a return type without those.
    _return_type: CppType  # use the property return_type!

    _parameter_list: CppParameterList  # this is private: use the property parameter_list
    function_name: str
    is_pure_virtual: bool

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self._init_template_host()
        self.specifiers: List[str] = []
        self.is_pure_virtual = False
        self.function_name = ""

    @property
    def return_type(self) -> CppType:
        return self._return_type

    @return_type.setter
    def return_type(self, new_return_type: CppType) -> None:
        self._return_type = new_return_type
        self._return_type.parent = self

    @property
    def parameter_list(self) -> CppParameterList:
        return self._parameter_list

    @parameter_list.setter
    def parameter_list(self, new_parameter_list: CppParameterList) -> None:
        self._parameter_list = new_parameter_list
        self._parameter_list.parent = self
        for param in self._parameter_list.parameters:
            param.parent = self._parameter_list

    def name(self) -> str:
        return self.function_name

    def qualified_function_name(self) -> str:
        parent_scope = self.cpp_scope(False).str_cpp()
        if len(parent_scope) == 0:
            return self.function_name
        else:
            return parent_scope + "::" + self.function_name

    def qualified_function_name_with_specialization(self) -> str:
        return self.qualified_function_name() + self.str_template_specialization()

    def function_name_with_specialization(self) -> str:
        return self.function_name + self.str_template_specialization()

    def with_specialized_template(self, template_specs: CppTemplateSpecialization) -> Optional[CppFunctionDecl]:
        """Returns a new partially or fully specialized template function, implemented for the given type
        Returns None if the type(s) provided by template_specs is not used by this function.
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

    def with_qualified_types(self, current_scope: Optional[CppScope] = None) -> CppFunctionDecl:
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
        new_function_decl = copy.deepcopy(self)

        if hasattr(self, "return_type"):
            new_function_decl.return_type = self.return_type.with_qualified_types(current_scope)
            if new_function_decl.return_type is not self.return_type:
                was_changed = True

        new_function_decl.parameter_list = self.parameter_list.with_qualified_types(current_scope)
        if new_function_decl.parameter_list is not self.parameter_list:
            was_changed = True

        if was_changed:
            return new_function_decl
        else:
            return self

    def is_inferred_return_type(self) -> bool:
        if not hasattr(self, "return_type"):
            return False
        return self.return_type.typenames == ["auto"]

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
            specifiers_strs = list(map(str, self.specifiers))
            if len(specifiers_strs) > 0 and len(r) > 0:
                r += " "
            r = r + " ".join(specifiers_strs)

        return r

    # def is_auto_decl(self):
    #     self.return_type.typenames[0]

    def str_code(self) -> str:
        r = self._str_signature() + ";"
        return r

    def str_full_return_type(self) -> str:
        """The C++ return type of the function, without API, virtual or inline specifiers"""
        if self.is_destructor():
            return ""
        r = self.return_type.str_return_type()
        for prefix in self.options.functions_api_prefixes_list():
            r = r.replace(prefix + " ", "")
        return r

    def is_const(self) -> bool:
        return "const" in self.specifiers

    def is_method(self) -> bool:
        from srcmlcpp.cpp_types.blocks.cpp_public_protected_private import CppPublicProtectedPrivate

        assert hasattr(self, "parent")
        is_method = isinstance(self.parent, CppPublicProtectedPrivate)
        return is_method

    def method_access_type(self) -> CppAccessType:
        """
        Returns "public", "private", or "protected"
        Will throw if this is not a method!
        """
        from srcmlcpp.cpp_types.blocks.cpp_public_protected_private import CppPublicProtectedPrivate

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
        is_virtual = "virtual" in self.return_type.specifiers or "override" in self.specifiers
        return is_virtual

    def is_overloaded_method(self) -> bool:
        if not self.is_method():
            return False
        parent_struct = self.parent_struct_if_method()
        assert parent_struct is not None
        methods_same_name = parent_struct.get_methods_with_name(self.function_name)
        assert len(methods_same_name) >= 1
        is_overloaded = len(methods_same_name) >= 2
        return is_overloaded

    def parent_struct_if_method(self) -> Optional[CppStruct]:
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
        from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock

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

    def access_type_if_method(self) -> Optional[CppAccessType]:
        from srcmlcpp.cpp_types.blocks.cpp_public_protected_private import CppPublicProtectedPrivate

        if not self.is_method():
            return None
        ppp = self.parent
        assert isinstance(ppp, CppPublicProtectedPrivate)
        r = ppp.access_type
        return r

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

    def is_destructor(self) -> bool:
        r = self.function_name.startswith("~")
        if r:
            assert self.is_method()
        return r

    def is_default_constructor(self) -> bool:
        if not self.is_constructor():
            return False
        nb_params = len(self.parameter_list.parameters)
        return nb_params == 0

    def is_copy_constructor(self) -> bool:
        if not self.is_constructor():
            return False
        if len(self.parameter_list.parameters) != 1:
            return False

        parent_struct_name = self.parent_struct_name_if_method()
        assert parent_struct_name is not None
        param_type = self.parameter_list.parameters[0].decl.cpp_type

        is_same_type = param_type.typenames == [parent_struct_name]
        is_const_ref = "const" in param_type.specifiers and param_type.modifiers == ["&"]
        is_pass_by_copy = len(param_type.specifiers) == 0 and len(param_type.modifiers) == 0

        is_copy_ctor = is_same_type and (is_const_ref or is_pass_by_copy)
        return is_copy_ctor

    def is_operator(self) -> bool:
        return self.function_name.startswith("operator")

    def operator_name(self) -> str:
        assert self.is_operator()
        r = self.function_name[len("operator") :].strip()
        return r

    def returns_pointer(self) -> bool:
        r = hasattr(self, "return_type") and self.return_type.modifiers == ["*"]
        return r

    def returns_pointer_to_pointer(self) -> bool:
        r = hasattr(self, "return_type") and self.return_type.modifiers.count("*") == 2
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
        return self.str_code()

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
