from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base.cpp_element import CppElement

from dataclasses import dataclass


@dataclass
class _ScopedIdentifier:
    scope: CppScope
    identifier: str


def current_token_matches_scoped_identifier(
    scoped_identifier: _ScopedIdentifier, current_scope: CppScope, current_token: str
) -> bool:
    """
    namespace A { enum E { Foo }; }
    namespace B {
        enum class  BE { Foo };
        namespace C {
            struct S { BE be = BE::Foo; };
                                 ^
    }
    """
    # scoped_identifier.scope = B::BE
    # scoped_identifier.identifier = Foo
    # current_scope = B::C::S
    # current_token = BE::Foo
    # => can access, because
    #       current_scope[:1] + current_token = B::BE::Foo
    if current_token.startswith("::"):
        return False

    current_scopes = current_scope.scope_hierarchy_list()
    scoped_identifier_qualified_name = scoped_identifier.scope.qualified_name(scoped_identifier.identifier)
    for current_scope_prefix in current_scopes:
        current_token_proposed_qualified_name = current_scope_prefix.qualified_name(current_token)
        if current_token_proposed_qualified_name == scoped_identifier_qualified_name:
            return True
    return False


def apply_scoped_identifiers_to_code(
    cpp_code: str, current_scope: CppScope, scoped_identifiers: list[_ScopedIdentifier]
) -> str:
    """
    Parse cpp_code character by character, updates current_scoped_identifier in the loop

    Each time a new current_scoped_identifier is collected, apply_scoped_identifier() is called,
    and the result is added to the new code.

    Examples:
        scoped_identifier = "SubNamespace::Foo"
        qualified_scoped_identifier = "Main::SubNamespace::Foo"
        => "Main::SubNamespace::Foo" (we can add more scope)

        scoped_identifier = "Foo"
        qualified_scoped_identifier = "Main::SubNamespace::Foo"
        => "Main::SubNamespace::Foo" (we can add more scope)

        scoped_identifier = "::Foo"
        qualified_scoped_identifier = "Main::SubNamespace::Foo"
        => "::Foo" (we can't add scope to the root)

        scoped_identifier = "Other::Foo"
        qualified_scoped_identifier = "Main::Foo"
        => "Other::Foo" (we can't add more scope)
    """
    new_code = ""
    current_token = ""
    i = 0
    in_string = False
    in_comment = False

    while i < len(cpp_code):
        char = cpp_code[i]

        # Check for string literal start/end
        if char == '"' and not in_comment:
            in_string = not in_string

        # Check for comment start
        if char == "/" and i + 1 < len(cpp_code) and cpp_code[i + 1] == "/" and not in_string:
            in_comment = True

        # Process characters outside strings and comments
        if not in_string and not in_comment:
            if char.isalnum() or char == "_":
                current_token += char
            elif char == ":" and i + 1 < len(cpp_code) and cpp_code[i + 1] == ":":
                current_token += "::"
                i += 1
            else:
                if current_token:
                    # This is the heart of the algorithm, which is not placed in a sub-function
                    # for performance reasons

                    # current_token is a scoped identifier found in the C++ code
                    # for example `Foo` or `::Foo` or `SubNamespace::Foo`

                    # scoped_identifier.scope = N
                    # current_scope = A::ClassNoDefaultCtor
                    # current_token = foo
                    # => can't access

                    # scoped_identifier.scope = N
                    # current_scope = A::ClassNoDefaultCtor
                    # current_token = N::Foo
                    # => can access

                    # for qualified_identifier in qualified_scoped_identifiers:
                    #     if not current_token.startswith("::"):
                    #         if qualified_identifier.endswith("::" + current_token):
                    #             current_token = qualified_identifier
                    for scoped_identifier in scoped_identifiers:
                        if current_token_matches_scoped_identifier(scoped_identifier, current_scope, current_token):
                            scoped_identifier_qualified_name = scoped_identifier.scope.qualified_name(
                                scoped_identifier.identifier
                            )
                            current_token = scoped_identifier_qualified_name

                            # scoped_identifier.scope = N
                            # current_scope = A::ClassNoDefaultCtor
                            # current_token = N::Foo
                            # => can access
                            # => can access if current_token starts with "scoped_identifier.scope::"

                    new_code += current_token
                    current_token = ""
                new_code += char
        else:
            new_code += char

        # Reset in_comment at the end of the line
        if char == "\n":
            in_comment = False

        i += 1

    # Add the last token if it exists
    if current_token:
        # This is the heart of the algorithm, which is not placed in a sub-function
        # for performance reasons
        # for qualified_identifier in qualified_scoped_identifiers:
        #     if not current_token.startswith("::"):
        #         if qualified_identifier.endswith("::" + current_token):
        #             current_token = qualified_identifier
        # new_code += current_token
        for scoped_identifier in scoped_identifiers:
            if current_token_matches_scoped_identifier(scoped_identifier, current_scope, current_token):
                scoped_identifier_qualified_name = scoped_identifier.scope.qualified_name(scoped_identifier.identifier)
                current_token = scoped_identifier_qualified_name

        new_code += current_token

    return new_code


class CppScopeIdentifiers:
    _scoped_identifiers: list[_ScopedIdentifier]

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
                self._scoped_identifiers.append(_ScopedIdentifier(element_scope, identifier_name))

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
        new_code = apply_scoped_identifiers_to_code(new_code, current_scope, self._scoped_identifiers)
        return new_code
