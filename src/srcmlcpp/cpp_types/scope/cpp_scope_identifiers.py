from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base.cpp_element import CppElement


def apply_scoped_identifiers_to_code(cpp_code: str, qualified_scoped_identifiers: list[str]) -> str:
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
                    for qualified_identifier in qualified_scoped_identifiers:
                        if not current_token.startswith("::"):
                            if qualified_identifier.endswith("::" + current_token):
                                current_token = qualified_identifier

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
        for qualified_identifier in qualified_scoped_identifiers:
            if not current_token.startswith("::"):
                if qualified_identifier.endswith("::" + current_token):
                    current_token = qualified_identifier
        new_code += current_token

    return new_code


class CppScopeIdentifiers:
    _cache_qualified_identifiers: list[str]

    def __init__(self) -> None:
        self._cache_qualified_identifiers = []

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
                self._cache_qualified_identifiers.append(element_scope.qualified_name(identifier_name))

    def qualify_cpp_code(self, cpp_code: str, scope: CppScope) -> str:
        """
        cpp_code is an extract of C++ code that come from a declaration. It can either be a type or a value
        Example:
            std::vector<Main::Foo> fooList = Main::Foo::CreateFooList();
        In this example, it can be either `std::vector<Main::Foo> fooList` or `Main::Foo::CreateFooList()`

        Its current scope is scope

        qualify_cpp_code() should return the fully qualified version of cpp_code
        """
        new_code = cpp_code
        for qualified_identifier in self._cache_qualified_identifiers:
            new_code = apply_scoped_identifiers_to_code(new_code, [qualified_identifier])
        return new_code
