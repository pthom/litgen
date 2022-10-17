from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Union, cast

from srcmlcpp.cpp_types.base import *
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope
from srcmlcpp.cpp_types.functions import CppFunctionDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
    from srcmlcpp.cpp_types.cpp_enum import CppEnum
    from srcmlcpp.cpp_types.decls_types import CppDecl, CppDeclStatement

    KnownElementTypes = Union[CppStruct, CppFunctionDecl, CppDecl, CppEnum]
    KnownElementTypesList = List[KnownElementTypes]

__all__ = ["CppBlock"]


@dataclass
class CppBlock(CppElementAndComment):
    """The class CppBlock is a container that represents any set of code  detected by srcML.
    It has several derived classes.

     - For namespaces:
             Inside srcML we have this: <block>CODE</block>
             Inside python, the block is handled by `CppBlock`
     - For files (i.e "units"):
             Inside srcML we have this: <unit>CODE</unit>
             Inside python, the block is handled by `CppUnit` (which derives from `CppBlock`)
     - For functions and anonymous block:
             Inside srcML we have this:  <block><block_content>CODE</block_content></block>
             Inside python, the block is handled by `CppBlockContent` (which derives from `CppBlock`)
     - For classes and structs:
             Inside srcML we have this: <block><private or public>CODE</private or public></block>
             Inside python, the block is handled by `CppPublicProtectedPrivate` (which derives from `CppBlock`)

     https://www.srcml.org/doc/cpp_srcML.html#block
    """

    _block_children: List[CppElementAndComment]

    def __init__(self, element: SrcmlWrapper) -> None:
        dummy_cpp_comments = CppElementComments()
        super().__init__(element, dummy_cpp_comments)
        self._block_children: List[CppElementAndComment] = []

    @property
    def block_children(self) -> List[CppElementAndComment]:
        return self._block_children

    @block_children.setter
    def block_children(self, value: List[CppElementAndComment]) -> None:
        self._block_children = value
        self.fill_children_parents()

    def str_block(self, is_enum: bool = False) -> str:
        result = ""
        for i, child in enumerate(self.block_children):
            if i < len(self.block_children) - 1:
                child_str = child.str_commented(is_enum=is_enum)
            else:
                child_str = child.str_commented(is_enum=False)
            result += child_str
            if not child_str.endswith("\n"):
                result += "\n"
        return result

    def all_functions(self) -> List[CppFunctionDecl]:
        """Gathers all CppFunctionDecl and CppFunction in the children (non recursive)"""
        from srcmlcpp.cpp_types.functions.cpp_function_decl import CppFunctionDecl

        r: List[CppFunctionDecl] = []
        for child in self.block_children:
            if isinstance(child, CppFunctionDecl):
                r.append(child)
        return r

    def all_functions_with_name(self, name: str) -> List[CppFunctionDecl]:
        """Gathers all CppFunctionDecl and CppFunction matching a given name"""
        all_functions = self.all_functions()
        r: List[CppFunctionDecl] = []
        for fn in all_functions:
            if fn.function_name == name:
                r.append(fn)
        return r

    def all_structs_recursive(self) -> List[CppStruct]:
        """Gathers all CppStruct and CppClass in the children (*recursively*)"""
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct

        r_ = self.all_cpp_elements_recursive(wanted_type=CppStruct)
        r = [cast(CppStruct, v) for v in r_]
        return r

    def find_struct_or_class(
        self, class_name_with_scope: str, current_scope: Optional[CppScope] = None
    ) -> Optional[CppStruct]:
        """Given a current scope, look for an existing matching class
        class_name_with_scope is a name that could include additional scopes
        """
        if current_scope is None:
            current_scope = self.cpp_scope()
        if "::" in class_name_with_scope:
            items = class_name_with_scope.split("::")
            class_name = items[-1]
            class_scope_str = "::".join(items[:-1])
        else:
            class_name = class_name_with_scope
            class_scope_str = ""

        all_structs = self.all_structs_recursive()
        for struct in all_structs:

            current_scope_str = current_scope.str_cpp()

            searched_scopes_strs = []
            searched_scopes_strs.append(class_scope_str)
            if len(current_scope_str) > 0:
                searched_scopes_strs.append(current_scope_str + "::" + class_scope_str)

            struct_scope_str = struct.cpp_scope(include_self=False).str_cpp()

            is_struct_visible_from_scope = False
            for searched_scope_str in searched_scopes_strs:
                if searched_scope_str.startswith(struct_scope_str):
                    is_struct_visible_from_scope = True

            is_name_equal = struct.class_name == class_name

            if is_name_equal and is_struct_visible_from_scope:
                return struct

        return None

    def all_functions_recursive(self) -> List[CppFunctionDecl]:
        """Gathers all CppFunctionDecl and CppFunction in the children (*recursive*)"""
        r_ = self.all_elements_of_type(wanted_type=CppFunctionDecl)
        r = [cast(CppFunctionDecl, v) for v in r_]
        return r

    def all_decl_statement_recursive(self) -> List[CppDeclStatement]:
        """Gathers all CppDeclStatement in the children (*recursive*)"""
        from srcmlcpp.cpp_types.decls_types.cpp_decl_statement import CppDeclStatement

        r_ = self.all_elements_of_type(wanted_type=CppDeclStatement)
        r = [cast(CppDeclStatement, v) for v in r_]
        return r

    def all_decl_recursive(self) -> List[CppDecl]:
        """Gathers all CppDecl in the children (*recursive*)
        This can include decls from DeclStatements, function parameter, enum values, etc.
        """
        from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl

        r_ = self.all_elements_of_type(wanted_type=CppDecl)
        r = [cast(CppDecl, v) for v in r_]
        return r

    def is_function_overloaded(self, function: CppFunctionDecl) -> bool:
        functions_same_name = self.all_functions_with_name(function.function_name)
        assert len(functions_same_name) >= 1
        is_overloaded = len(functions_same_name) >= 2
        return is_overloaded

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        """Visits all the cpp children, and run the given function on them.
        Runs the visitor on this block first, then on its children
        """
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        for child in self.block_children:
            child.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def all_cpp_elements_recursive(self, wanted_type: Optional[type] = None) -> List[CppElement]:
        _all_cpp_elements = []

        def visitor_add_cpp_element(cpp_element: CppElement, event: CppElementsVisitorEvent, _depth: int) -> None:
            if event == CppElementsVisitorEvent.OnElement:
                if wanted_type is None or isinstance(cpp_element, wanted_type):
                    _all_cpp_elements.append(cpp_element)

        self.visit_cpp_breadth_first(visitor_add_cpp_element)
        return _all_cpp_elements

    def all_elements_of_type(self, wanted_type: type) -> List[CppElement]:
        return self.all_cpp_elements_recursive(wanted_type)

    def add_element(self, element: CppElementAndComment) -> None:
        element.parent = self
        self.block_children.append(element)

    def known_callables(self) -> KnownElementTypesList:
        """The subpart of the known elements that can be called via ()
        Simple:
            - Structs and classes, when calling their constructor via (...)
            - Functions and methods
        Declarations (CppDecl), only in certain cases:
            - when they are decl statement that defines a lambda, a std::function, etc.
              This case is too complex and not supported
        """
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
        from srcmlcpp.cpp_types.functions import CppFunctionDecl

        r: KnownElementTypesList = []
        all_elements = self.all_cpp_elements_recursive()
        for element in all_elements:
            if isinstance(element, (CppStruct, CppFunctionDecl)):
                r.append(element)
        return r

    def known_callables_init_list(self) -> KnownElementTypesList:
        """The subpart of the known elements that can be called via {}, i.e. structs and classes"""
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct

        r: KnownElementTypesList = []
        all_elements = self.all_cpp_elements_recursive()
        for element in all_elements:
            if isinstance(element, (CppStruct)):
                r.append(element)
        return r

    def known_values(self) -> KnownElementTypesList:
        """The subpart of the elements that declare variable,
        Declarations (CppDecl), only in certain cases:
            - When they are member of an Enum, Struct, Namespace
            - When they are inside a DeclStatement (which could also be a lambda decl)
            But *not* when they are function parameters!
        """
        from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl, CppDeclContext

        r: KnownElementTypesList = []
        all_elements = self.all_cpp_elements_recursive()
        for element in all_elements:
            if isinstance(element, CppDecl):
                """
                Declarations (CppDecl), only in certain cases:
                    - When they from a decl statement
                    - When they are inside a DeclStatement (which can be inside an Enum, Struct, Namespace)
                    But *not* when they are function parameters!
                """
                if element.decl_context() in [CppDeclContext.VarDecl, CppDeclContext.EnumDecl]:
                    r.append(element)
        return r

    def known_types(self) -> KnownElementTypesList:
        """The subpart of the elements that could be as a type.
        We do *not* support synonyms defined via `typedef` or `using` !
        """
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
        from srcmlcpp.cpp_types.cpp_enum import CppEnum

        r: KnownElementTypesList = []
        all_elements = self.all_cpp_elements_recursive()
        for element in all_elements:
            if isinstance(element, (CppStruct, CppEnum)):
                r.append(element)
        return r

    def __str__(self) -> str:
        return self.str_block()
