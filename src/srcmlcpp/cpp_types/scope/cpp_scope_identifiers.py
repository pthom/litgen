from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base.cpp_element import CppElement


def current_token_matches_scoped_identifier(
    scoped_identifier_qualified_name: str, current_scope: CppScope, current_token: str
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

    current_scopes = current_scope.scope_hierarchy_list
    for current_scope_prefix in current_scopes:
        current_token_proposed_qualified_name = current_scope_prefix.qualified_name(current_token)
        if current_token_proposed_qualified_name == scoped_identifier_qualified_name:
            return True
    return False


def apply_scoped_identifiers_to_code(
    cpp_code: str, current_scope: CppScope, scoped_identifier_qualified_names: list[str]
) -> str:
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
                    for scoped_identifier_qualified_name in scoped_identifier_qualified_names:
                        if current_token_matches_scoped_identifier(
                            scoped_identifier_qualified_name, current_scope, current_token
                        ):
                            current_token = scoped_identifier_qualified_name
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
        for scoped_identifier_qualified_name in scoped_identifier_qualified_names:
            if current_token_matches_scoped_identifier(scoped_identifier_qualified_name, current_scope, current_token):
                current_token = scoped_identifier_qualified_name

        new_code += current_token

    return new_code


# def _make_terse_scoped_identifier_kc(scoped_identifier: str, current_scope: CppScope) -> str:
#     """
#     Given a scoped_identifier, return a terse version of it, if possible given the current scope
#     Example:
#         scoped_identifier = "A::B::C"
#         current_scope = "A::B::C::D"
#         => "C"
#
#         scoped_identifier = "N1::N3::S3"
#         current_scope=  "N0::N1::N3"
#         => "S3"
#     """
#     result = scoped_identifier
#     current_scopes = current_scope.scope_hierarchy_list()
#     for current_scope_prefix in current_scopes:
#         if result.startswith(current_scope_prefix.str_cpp_prefix):
#             result = result[len(current_scope_prefix.str_cpp_prefix) :]
#     return result
#

# def _make_terse_scoped_identifier(scoped_identifier: str, current_scope: str) -> str:
#     scoped_parts = scoped_identifier.split('::')
#     scope_parts = current_scope.split('::')
#
#     # Check if scoped_identifier is a direct subset of current_scope
#     if all(part1 == part2 for part1, part2 in zip(scoped_parts, scope_parts)):
#         return scoped_parts[-1]
#
#     # Check for partial overlap from the right
#     for i in range(1, min(len(scoped_parts), len(scope_parts)) + 1):
#         if scoped_parts[-i] != scope_parts[-i]:
#             return '::'.join(scoped_parts[-i:])
#
#     return scoped_identifier


def _make_terse_scoped_identifier(scoped_identifier: str, current_scope: str) -> str:
    identifier_parts = scoped_identifier.split("::")
    scope_parts = current_scope.split("::")

    # if current_scope = 'NA::N0::N1::N3'
    # and scoped_identifier =    'N1::N2::S2::s1'
    # We need to remove NA::N0 from current scope
    identifier_first_part = identifier_parts[0]
    if identifier_first_part in scope_parts:
        idx = scope_parts.index(identifier_first_part)
        scope_parts = scope_parts[idx:]

    # To account for this test:
    # assert _make_terse_scoped_identifier(scoped_identifier = "N1::N3::S3", current_scope = "N0::N1::N3") == "S3"
    # take current_scope, and construct
    #    N0::N1::N3
    #    N1::N3
    #    N3
    for i in range(len(scope_parts)):
        scope_extract = "::".join(scope_parts[: len(scope_parts) - i]) + "::"  # will be "N0::N1::N3", "N1::N3", "N3"
        if scoped_identifier.startswith(scope_extract):
            r = scoped_identifier[len(scope_extract) :]
            return r

    for i in range(len(scope_parts)):
        scope_extract = "::".join(scope_parts[i:]) + "::"  # will be "N0::N1::N3", "N1::N3", "N3"
        if scoped_identifier.startswith(scope_extract):
            r = scoped_identifier[len(scope_extract) :]
            return r
    return scoped_identifier


def make_terse_code(cpp_code: str, current_scope: CppScope) -> str:
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
                    current_token = _make_terse_scoped_identifier(current_token, current_scope.str_cpp)
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
        current_token = _make_terse_scoped_identifier(current_token, current_scope.str_cpp)
        new_code += current_token

    return new_code


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
        new_code = apply_scoped_identifiers_to_code(new_code, current_scope, self._scoped_identifiers)
        return new_code
