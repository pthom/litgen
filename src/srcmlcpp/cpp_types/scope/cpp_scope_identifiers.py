from typing import Optional

from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base.cpp_element import CppElement


class CppScopeIdentifiers:
    _cache_known_identifiers_scope: dict[CppScope, list[str]]

    def __init__(self):
        self._cache_known_identifiers_scope = {}

    def fill_cache(self, all_elements: list[CppElement]) -> None:
        from srcmlcpp.cpp_types import CppStruct, CppFunctionDecl, CppEnum
        from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl, CppDeclContext

        for element in all_elements:
            element_scope = element.cpp_scope()
            shall_add = False
            # add all structs and enums
            if isinstance(element, (CppStruct, CppEnum)):
                shall_add = True
            # Add all functions, except constructors (which are callable via their class)
            if isinstance(element, CppFunctionDecl):
                if not element.is_constructor():
                    shall_add = True
            # Add decls, except function parameters
            if isinstance(element, CppDecl):
                # Declarations (CppDecl), only in certain cases:
                #    - When they from a decl statement
                #    - When they are inside a DeclStatement (which can be inside an Enum, Struct, Namespace)
                #    But *not* when they are function parameters!
                if element.decl_context() in [CppDeclContext.VarDecl, CppDeclContext.EnumDecl]:
                    shall_add = True

            if shall_add:
                assert isinstance(element, (CppStruct, CppFunctionDecl, CppDecl, CppEnum))
                identifier_name = element.name()

                def do_cache(cpp_scope: CppScope, scoped_identifier_name: str) -> None:
                    if cpp_scope not in self._cache_known_identifiers_scope:
                        self._cache_known_identifiers_scope[cpp_scope] = []
                    self._cache_known_identifiers_scope[cpp_scope].append(scoped_identifier_name)

                current_scope: Optional[CppScope] = element_scope
                scoped_identifier_name = identifier_name
                while current_scope is not None:
                    do_cache(current_scope, scoped_identifier_name)
                    if len(current_scope.scope_parts) > 0:
                        scoped_identifier_name = (
                            current_scope.scope_parts[-1].scope_name + "::" + scoped_identifier_name
                        )
                        current_scope = current_scope.parent_scope()
                    else:
                        current_scope = None

                # add identifier_name to the current scope and its parents,
                # after applying the scope resolution operator "::"

                # if element_scope not in self._cache_known_identifiers_scope:
                #     self._cache_known_identifiers_scope[element_scope] = []
                # self._cache_known_identifiers_scope[element_scope].append(identifier_name)

    def known_identifiers(self, scope: CppScope) -> list[str]:
        assert hasattr(self, "_cache_known_identifiers_scope")

        if scope not in self._cache_known_identifiers_scope:
            return []
        return self._cache_known_identifiers_scope[scope]
