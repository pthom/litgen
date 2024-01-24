# pyright: reportAttributeAccessIssue=false

from __future__ import annotations
import copy
from dataclasses import dataclass

import codemanip.code_utils
import srcmlcpp
from srcmlcpp.cpp_types.base import (
    CppElementComments,
    CppAccessType,
    CppElementAndComment,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.cpp_types.blocks import (
    CppBlock,
    CppPublicProtectedPrivate,
    CppUnit,
)
from srcmlcpp.cpp_types.classes.cpp_super_list import CppSuperList
from srcmlcpp.cpp_types.decls_types import CppDecl, CppDeclStatement
from srcmlcpp.cpp_types.functions import CppFunctionDecl
from srcmlcpp.cpp_types.template.cpp_i_template_host import CppITemplateHost
from srcmlcpp.cpp_types.template.cpp_template_specialization import CppTemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppStruct"]


@dataclass
class CppStruct(CppElementAndComment, CppITemplateHost):
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    class_name: str  # either the class or the struct name
    _super_list: CppSuperList
    _block: CppBlock
    specifier: str  # "final" for final classes, empty otherwise
    macro: str  # used in rare cases, such as `struct MY_API Foo { };` where macro will be "MY_API"

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self._init_template_host()
        self.class_name = ""
        self.specifier = ""

    @property
    def super_list(self) -> CppSuperList:
        return self._super_list

    @super_list.setter
    def super_list(self, value: CppSuperList) -> None:
        self._super_list = value
        self.fill_children_parents()

    @property
    def block(self) -> CppBlock:
        return self._block

    @block.setter
    def block(self, value: CppBlock) -> None:
        self._block = value
        self.fill_children_parents()

    def name(self) -> str:
        return self.class_name

    def str_code(self) -> str:
        from srcmlcpp.cpp_types.classes.cpp_class import CppClass

        r = ""
        r += self.str_template()

        if isinstance(self, CppClass):
            r += "class "
        elif isinstance(self, CppStruct):
            r += "struct "
        r += f"{self.class_name}"

        if hasattr(self, "super_list") and len(str(self.super_list)) > 0:
            r += str(self.super_list)

        r += "\n"

        r += "{\n"
        # "public:", "private:", "protected:" are not indented, but their descendants are
        r += str(self.block)
        r += "};\n"

        return r

    def __str__(self) -> str:
        return self.str_commented()

    def __repr__(self):
        r = "struct " + self.class_name
        return r

    def is_final(self) -> bool:
        return self.specifier == "final"

    def qualified_class_name(self) -> str:
        parent_scope = self.cpp_scope(False).str_cpp
        if len(parent_scope) == 0:
            return self.class_name
        else:
            return parent_scope + "::" + self.class_name

    def qualified_class_name_with_specialization(self) -> str:
        return self.qualified_class_name() + self.str_template_specialization()

    def class_name_with_specialization(self) -> str:
        return self.class_name + self.str_template_specialization()

    def has_base_classes(self) -> bool:
        if not hasattr(self, "super_list"):
            return False
        return len(self.super_list.super_list) > 0

    def base_classes(self) -> list[tuple[CppAccessType, CppStruct]]:
        if not self.has_base_classes():
            return []

        r = []
        for cpp_super in self.super_list.super_list:
            access_type = CppAccessType.from_name(cpp_super.specifier)

            root_cpp_unit = CppUnit.find_root_cpp_unit(self)
            base_struct = root_cpp_unit.find_struct_or_class(
                cpp_super.superclass_name, self.cpp_scope(include_self=False)
            )
            if base_struct is not None:
                r.append((access_type, base_struct))
        return r

    def has_user_defined_default_constructor_zero_param(self) -> bool:
        for method in self.get_methods():
            if method.is_default_constructor_zero_param():
                return True
        return False

    def has_user_defined_default_constructor_non_zero_param(self) -> bool:
        for method in self.get_methods():
            if method.is_constructor() and len(method.parameter_list.parameters) > 0:
                return True
        return False

    def has_user_defined_default_constructor(self) -> bool:
        for method in self.get_methods():
            if method.is_default_constructor():
                return True
        return False

    def has_user_defined_constructor(self) -> bool:
        for method in self.get_methods():
            if method.is_constructor():
                return True
        return False

    def has_deleted_default_constructor(self) -> bool:
        for method in self.get_methods():
            if method.is_default_constructor() and "delete" in method.specifiers:
                return True
        return False

    def get_user_defined_copy_constructor(self) -> CppFunctionDecl | None:
        for method in self.get_methods():
            if method.is_copy_constructor():
                return method
        return None

    def is_user_defined_copy_constructor_part_of_api(self) -> bool:
        """If there is a user defined copy constructor, is it public and not deleted?"""
        user_defined_copy_constructor = self.get_user_defined_copy_constructor()
        assert user_defined_copy_constructor is not None
        access_type = user_defined_copy_constructor.method_access_type()
        if access_type != CppAccessType.public:
            return False
        if "delete" in user_defined_copy_constructor.specifiers:
            return False
        return True

    def has_private_destructor(self) -> bool:
        r = False
        for method in self.get_methods():
            if method.is_destructor():
                access_type = method.access_type_if_method()
                assert access_type is not None
                if access_type == CppAccessType.private:
                    r = True
        return r

    def get_access_blocks(self, access_type: CppAccessType | None) -> list[CppPublicProtectedPrivate]:
        """
        Returns the public blocks of the class
        """
        r: list[CppPublicProtectedPrivate] = []
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                if access_type is None or access_zone.access_type == access_type:
                    r.append(access_zone)
        return r

    def get_members_with_access_type(self) -> list[tuple[CppAccessType, CppDecl]]:
        r: list[tuple[CppAccessType, CppDecl]] = []
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                access_type = access_zone.access_type
                for child in access_zone.block_children:
                    if isinstance(child, CppDeclStatement):
                        for cpp_decl in child.cpp_decls:
                            r.append((access_type, cpp_decl))
        return r

    def get_members(self, access_type: CppAccessType | None = None) -> list[CppDecl]:
        r: list[CppDecl] = []
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                if access_type is None or access_type == access_zone.access_type:
                    for child in access_zone.block_children:
                        if isinstance(child, CppDeclStatement):
                            for cpp_decl in child.cpp_decls:
                                r.append(cpp_decl)
        return r

    def get_elements(
        self, access_type: CppAccessType | None = None, element_type: type | None = None
    ) -> list[CppElementAndComment]:
        """
        Returns all the elements of this struct
        (include members, methods, inner struct)
        """
        r: list[CppElementAndComment] = []
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                if access_type is not None:
                    if access_zone.access_type != access_type:
                        continue
                for child in access_zone.block_children:
                    if element_type is not None:
                        if isinstance(child, element_type):
                            r.append(child)
                    else:
                        r.append(child)
        return r

    def get_methods(self) -> list[CppFunctionDecl]:
        from srcmlcpp.cpp_types.functions.cpp_function_decl import CppFunctionDecl

        r: list[CppFunctionDecl] = []
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                for child in access_zone.block_children:
                    if isinstance(child, CppFunctionDecl):
                        r.append(child)
        return r

    def add_access_block(
        self, access_type: CppAccessType, comments: CppElementComments | None = None
    ) -> CppPublicProtectedPrivate:
        # Create ppp_block (CppPublicProtectedPrivate) via C++ code:
        code = codemanip.code_utils.unindent_code(access_type.name + ":")
        cpp_unit = srcmlcpp.code_to_cpp_unit(self.options, code)
        assert len(cpp_unit.block_children) == 1
        ppp_block = cpp_unit.block_children[0]
        assert isinstance(ppp_block, CppPublicProtectedPrivate)

        # Set comments
        if comments is not None:
            ppp_block.cpp_element_comments = comments

        # Store and return block
        self.block.add_element(ppp_block)
        return ppp_block

    def add_method(
        self,
        cpp_code: str,
        access_type: CppAccessType = CppAccessType.public,
        comments: CppElementComments | None = None,
    ) -> CppFunctionDecl:
        access_blocks = self.get_access_blocks(access_type=access_type)
        if len(access_blocks) == 0:
            self.add_access_block(access_type)

        access_block = self.get_access_blocks(access_type)[-1]

        fn = srcmlcpp.srcmlcpp_main.code_first_function_decl(self.options, cpp_code)
        if comments is not None:
            fn.cpp_element_comments = comments

        access_block.add_element(fn)

        return fn

    def get_methods_with_name(self, name: str) -> list[CppFunctionDecl]:
        all_methods = self.get_methods()
        r: list[CppFunctionDecl] = []
        for fn in all_methods:
            if fn.function_name == name:
                r.append(fn)
        return r

    def is_virtual(self) -> bool:
        """Returns True if there is at least one virtual method"""
        for method in self.get_methods():
            if method.is_virtual_method():
                return True
        return False

    def virtual_methods(self, include_inherited_virtual_methods: bool) -> list[CppFunctionDecl]:
        virtual_methods = []
        for base_method in self.get_methods():
            if base_method.is_virtual_method():
                virtual_methods.append(base_method)

        def is_method_already_present(method: CppFunctionDecl) -> bool:
            for present_method in virtual_methods:
                same_name = present_method.function_name == method.function_name
                same_parameters_types = (
                    present_method.parameter_list.str_types_names_only() == method.parameter_list.str_types_names_only()
                )
                if same_name and same_parameters_types:
                    return True
            return False

        for _access_type, base_class in self.base_classes():
            for base_method in base_class.virtual_methods(include_inherited_virtual_methods):
                if not is_method_already_present(base_method):
                    virtual_methods.append(base_method)

        return virtual_methods

    def _fill_children_parents(self) -> None:
        self.block.parent = self
        for ppp_block in self.block.block_children:
            assert isinstance(ppp_block, CppPublicProtectedPrivate)
            ppp_block.fill_children_parents()
            ppp_block.parent = self.block

    def with_specialized_template(self, template_specs: CppTemplateSpecialization) -> CppStruct | None:
        """Returns a new partially or fully specialized class, implemented for the given type
        Will return None if the application of the template changes nothing
        """
        new_class = copy.deepcopy(self)
        new_class._store_template_specs(template_specs)

        was_changed = False

        for ppp_new_block in new_class.block.block_children:
            if isinstance(ppp_new_block, CppPublicProtectedPrivate):
                ppp_new_block_children: list[CppElementAndComment] = []
                for ppp_child in ppp_new_block.block_children:
                    new_ppp_child: CppElementAndComment | None = None
                    if isinstance(ppp_child, (CppFunctionDecl, CppStruct, CppDeclStatement)):
                        new_ppp_child = ppp_child.with_specialized_template(template_specs)
                    if new_ppp_child is not None:
                        ppp_new_block_children.append(new_ppp_child)
                        was_changed = True
                    else:
                        ppp_new_block_children.append(ppp_child)
                ppp_new_block.block_children = ppp_new_block_children

        if was_changed:
            new_class._fill_children_parents()
            return new_class
        else:
            return None

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "super_list"):
            self.super_list.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        if hasattr(self, "block"):
            self.block.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        if hasattr(self, "template"):
            self.template.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
