from srcmlcpp.cpp_types.scope.cpp_scope import CppScope


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
