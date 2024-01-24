from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base.cpp_element import CppElement
from srcmlcpp.cpp_types.scope.cpp_scope_process import apply_scoped_identifiers_to_code


class CppScopeIdentifiers:
    _scoped_identifiers: list[str]

    def __init__(self) -> None:
        self._scoped_identifiers = []

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
                qualified_identifier = element_scope.qualified_name(identifier_name)
                self._scoped_identifiers.append(qualified_identifier)

    def qualify_cpp_code(self, cpp_code: str, current_scope: CppScope) -> str:
        """
        cpp_code is an extract of C++ code that come from a declaration. It can either be a type or a value
        Example:
            std::vector<Main::Foo> fooList = Main::Foo::CreateFooList();
        In this example, it can be either `std::vector<Main::Foo> fooList` or `Main::Foo::CreateFooList()`

        Its current scope is scope

        qualify_cpp_code() should return the fully qualified version of cpp_code
        """
        new_code = cpp_code

        # cached_scope = N
        # scope = A::ClassNoDefaultCtor
        # scoped_identifier = foo
        # => can't access

        # cached_scope = N
        # scope = A::ClassNoDefaultCtor
        # scoped_identifier = N::Foo
        # => can access
        new_code = apply_scoped_identifiers_to_code(
            new_code, current_scope.scope_hierarchy_prefix_list, self._scoped_identifiers
        )
        return new_code
