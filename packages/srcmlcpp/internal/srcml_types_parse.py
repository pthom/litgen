"""
This is the heart of the parsing of a xml tree into a tree of Cpp Elements (defined in srcml_types).

The main interface of this module is:
    parse_unit(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppUnit

All the other functions can be considered private to this module.
"""
from srcmlcpp.srcml_types import *
from srcmlcpp.srcml_xml_wrapper import SrcMlExceptionDetailed, emit_warning_if_not_quiet
from srcmlcpp.internal import srcml_caller, srcml_utils
from srcmlcpp.internal import srcml_comments


def parse_unprocessed(options: SrcmlOptions, element_c: CppElementAndComment) -> CppUnprocessed:  # noqa
    result = CppUnprocessed(element_c, element_c.cpp_element_comments)
    result.code = srcml_caller.srcml_to_code(element_c.srcml_xml)
    return result


def parse_type(options: SrcmlOptions, element: SrcmlXmlWrapper, previous_decl: Optional[CppDecl]) -> CppType:
    """
    https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """

    def recompose_type_name(element: SrcmlXmlWrapper) -> str:
        element_text = element.text()
        if element_text is None:
            # case for composed type
            return element.str_code_verbatim().strip()
        else:
            return element_text

    assert element.tag() == "type"
    result = CppType(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            typename = recompose_type_name(child)
            result.typenames.append(typename)
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            result.specifiers.append(child_text)
        elif child_tag == "modifier":
            modifier_text = child.text()
            assert modifier_text is not None
            if modifier_text not in CppType.authorized_modifiers():
                raise SrcMlExceptionDetailed(child, f'modifier "{modifier_text}" is not authorized')
            result.modifiers.append(modifier_text)
        # elif child_tag == "argument_list":
        #     result.argument_list.append(child.text)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    if len(result.typenames) == 0 and "..." not in result.modifiers:
        if previous_decl is None:
            raise SrcMlExceptionDetailed(result, "Can't find type name")
        assert previous_decl is not None
        result.typenames = previous_decl.cpp_type.typenames

    if len(result.typenames) == 0 and "..." not in result.modifiers:
        raise SrcMlExceptionDetailed(result, "len(result.names) == 0!")

    # process api names
    for name in result.typenames:
        is_api_name = False
        for api_prefix in options.functions_api_prefixes:
            if name.startswith(api_prefix):
                is_api_name = True
        if is_api_name:
            result.typenames.remove(name)
            result.specifiers = [name] + result.specifiers

    return result


def _parse_init_expr(element: SrcmlXmlWrapper) -> str:
    """
    Can parse simple literals, like "hello", whose tree looks like:
            <ns0:expr>
               <ns0:literal type="string">&quot;hello&quot;</ns0:literal>
            </ns0:expr>

    But for more complete expressions, like "1<<20", whose tree looks like:
            <ns0:expr>
                <ns0:literal type="number">1</ns0:literal>
                <ns0:operator><</ns0:operator>
                <ns0:literal type="number">20</ns0:literal>
            </ns0:expr>
    we will call srcml_to_code, which will invoke the executable srcml
    """
    assert element.tag() == "init"

    def expr_literal_value(expr_element: ET.Element) -> Optional[str]:
        # Case for simple literals
        if len(expr_element) != 1:
            return None
        else:
            for expr_child in expr_element:
                if srcml_utils.clean_tag_or_attrib(expr_child.tag) in [
                    "literal",
                    "name",
                ]:
                    if expr_child.text is not None:
                        return expr_child.text
        return None

    expr = srcml_utils.child_with_tag(element.srcml_xml, "expr")
    if expr is not None:
        eval_literal_value = expr_literal_value(expr)
        if eval_literal_value is not None:
            r = eval_literal_value
        else:
            r = srcml_caller.srcml_to_code(expr)
    else:
        r = element.str_code_verbatim().strip()
        if r.startswith("="):
            r = r[1:]

    return r


def _parse_name(element: SrcmlXmlWrapper) -> str:
    assert element.tag() == "name"
    element_text = element.text()
    if element_text is None:
        # composed name
        name = element.str_code_verbatim().strip()
    else:
        name = element_text
    return name


def parse_decl(
    options: SrcmlOptions,
    element_c: CppElementAndComment,
    previous_decl: Optional[CppDecl],
) -> CppDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    assert element_c.tag() == "decl"
    result = CppDecl(element_c, element_c.cpp_element_comments)
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "type":
            result.cpp_type = parse_type(options, child, previous_decl)
        elif child_tag == "name":
            decl_name_and_array = _parse_name(child)
            if "[" in decl_name_and_array and decl_name_and_array.endswith("]"):
                pos = decl_name_and_array.index("[")
                result.decl_name = decl_name_and_array[:pos]
                result.c_array_code = decl_name_and_array[pos:]
            else:
                result.decl_name = decl_name_and_array
        elif child_tag == "init":
            result.initial_value_code = _parse_init_expr(child)
        elif child_tag == "range":
            # this is for C bit fields
            result.bitfield_range = child.str_code_verbatim()
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_decl_stmt(options: SrcmlOptions, element_c: CppElementAndComment) -> CppDeclStatement:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """
    assert element_c.tag() == "decl_stmt"

    previous_decl: Optional[CppDecl] = None
    result = CppDeclStatement(element_c, element_c.cpp_element_comments)
    for child in element_c.make_wrapped_children():
        child_c = element_c
        child_c.srcml_xml = child.srcml_xml
        if child_c.tag() == "decl":
            child_name = child_c.name_code()
            assert child_name is not None
            cpp_decl = parse_decl(options, child_c, previous_decl)
            result.cpp_decls.append(cpp_decl)
            previous_decl = cpp_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_c.tag()}")

    # the comments were copied to all the internal decls, we can remove them from the decl_stmt
    result.cpp_element_comments = CppElementComments()

    return result


def parse_parameter(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppParameter:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element.tag() == "parameter"
    result = CppParameter(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "decl":
            child_c = CppElementAndComment(child, CppElementComments())
            result.decl = parse_decl(options, child_c, None)
        elif child_tag == "type":
            result.template_type = parse_type(options, child, None)  # This is only for template parameters
        elif child_tag == "name":
            child_text = child.text()
            assert child_text is not None
            result.template_name = child_text  # This is only for template parameters
        elif child_tag == "function_decl":
            raise SrcMlExceptionDetailed(child, "Can't use a function_decl as a param.")
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_parameter_list(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppParameterList:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element.tag() == "parameter_list"
    result = CppParameterList(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "parameter":
            result.parameters.append(parse_parameter(options, child))
        else:
            raise SrcMlExceptionDetailed(child, "unhandled tag")
    return result


def parse_template(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppTemplate:
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """
    assert element.tag() == "template"
    result = CppTemplate(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "parameter_list":
            result.parameter_list = parse_parameter_list(options, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


def fill_function_decl(
    options: SrcmlOptions,
    element_c: CppElementAndComment,
    function_decl: CppFunctionDecl,
) -> None:
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "type":
            if not hasattr(function_decl, "return_type") or len(function_decl.return_type.typenames) == 0:
                parsed_type = parse_type(options, child, None)
                function_decl.return_type = parsed_type
            else:
                additional_type = parse_type(options, child, None)
                function_decl.return_type.typenames += additional_type.typenames
        elif child_tag == "name":
            function_decl.function_name = _parse_name(child)
        elif child_tag == "parameter_list":
            function_decl.parameter_list = parse_parameter_list(options, child)
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            function_decl.specifiers.append(child_text)
        elif child_tag == "attribute":
            pass  # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag == "template":
            function_decl.template = parse_template(options, child)
        elif child_tag == "block":
            pass  # will be handled by parse_function
        elif child_tag == "modifier":
            raise SrcMlExceptionDetailed(child, "C style function pointers are poorly supported")
        elif child_tag == "comment":
            function_decl.cpp_element_comments.add_eol_comment(child.text)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    if len(function_decl.return_type.typenames) >= 2 and function_decl.return_type.typenames[0] == "auto":
        function_decl.return_type.typenames = function_decl.return_type.typenames[1:]


def parse_function_decl(options: SrcmlOptions, element_c: CppElementAndComment) -> CppFunctionDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element_c.tag() == "function_decl"
    result = CppFunctionDecl(element_c, element_c.cpp_element_comments)
    fill_function_decl(options, element_c, result)
    return result


def parse_function(options: SrcmlOptions, element_c: CppElementAndComment) -> CppFunction:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() == "function"
    result = CppFunction(element_c, element_c.cpp_element_comments)
    fill_function_decl(options, element_c, result)

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "block":
            child_c = CppElementAndComment(child, CppElementComments())
            result.block = parse_unprocessed(options, child_c)
        elif child_tag in [
            "type",
            "name",
            "parameter_list",
            "specifier",
            "attribute",
            "template",
            "comment",
        ]:
            pass  # already handled by fill_function_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


###############################################


def fill_constructor_decl(
    options: SrcmlOptions,
    element_c: CppElementAndComment,
    constructor_decl: CppConstructorDecl,
) -> None:
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            constructor_decl.function_name = _parse_name(child)
        elif child_tag == "parameter_list":
            constructor_decl.parameter_list = parse_parameter_list(options, child)
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            constructor_decl.specifiers.append(child_text)
        elif child_tag == "attribute":
            pass  # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag in ["block", "member_init_list"]:
            pass  # will be handled by parse_constructor
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")


def parse_constructor_decl(options: SrcmlOptions, element_c: CppElementAndComment) -> CppConstructorDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """
    assert element_c.tag() == "constructor_decl"
    result = CppConstructorDecl(element_c, element_c.cpp_element_comments)
    fill_constructor_decl(options, element_c, result)
    return result


def parse_constructor(options: SrcmlOptions, element_c: CppElementAndComment) -> CppConstructor:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() == "constructor"
    result = CppConstructor(element_c, element_c.cpp_element_comments)
    fill_constructor_decl(options, element_c, result)

    for child in element_c.make_wrapped_children():
        child_c = CppElementAndComment(child, CppElementComments())
        child_tag = child.tag()
        if child_tag == "block":
            result.block = parse_unprocessed(options, child_c)
        elif child_tag == "member_init_list":
            result.member_init_list = parse_unprocessed(options, child_c)
        elif child_tag in ["name", "parameter_list", "specifier", "attribute"]:
            pass  # alread handled by fill_constructor_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_super(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppSuper:
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert element.tag() == "super"
    result = CppSuper(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            result.specifier = child_text
        elif child_tag == "name":
            result.superclass_name = _parse_name(child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_super_list(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppSuperList:
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert element.tag() == "super_list"
    result = CppSuperList(element)
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "super":
            result.super_list.append(parse_super(options, child))
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def _add_comment_child_before_block(element_c: CppElementAndComment, child: SrcmlXmlWrapper):
    """
    For struct, enum and namespace, we might add a comment like this:
        struct Foo   // MY_API
        {
            ...
        };
    This comment was not added as an end of line comment previously, so that we add it now
    """
    assert child.tag() == "comment"
    child_text = child.text()
    assert child_text is not None
    comment_text = code_utils.cpp_comment_remove_comment_markers(child_text)
    if len(element_c.cpp_element_comments.comment_end_of_line) > 0:
        element_c.cpp_element_comments.comment_end_of_line += " - "
    element_c.cpp_element_comments.comment_end_of_line += comment_text


def parse_struct_or_class(options: SrcmlOptions, element_c: CppElementAndComment) -> CppStruct:
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """
    element_tag = element_c.tag()
    assert element_tag in ["struct", "class"]
    if element_tag == "struct":
        result = CppStruct(element_c, element_c.cpp_element_comments)
    else:
        result = CppClass(element_c, element_c.cpp_element_comments)

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.class_name = _parse_name(child)
        elif child_tag == "super_list":
            result.super_list = parse_super_list(options, child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        elif child_tag == "template":
            result.template = parse_template(options, child)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        elif child_tag == "decl":
            raise SrcMlExceptionDetailed(child, "Skipped struct because it misses a ';' at the end")
        else:
            raise SrcMlExceptionDetailed(child, "unhandled tag {child_tag}")

    return result


def parse_public_protected_private(options: SrcmlOptions, element_c: CppElementAndComment) -> CppPublicProtectedPrivate:
    """
    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types
    """
    access_type = element_c.tag()
    assert access_type in ["public", "protected", "private"]
    type = element_c.attribute_value("type")
    block_content = CppPublicProtectedPrivate(element_c, access_type, type)
    fill_block(options, element_c, block_content)
    return block_content


def parse_block(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppBlock:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block
    """
    assert element.tag() == "block"

    cpp_block = CppBlock(element)
    fill_block(options, element, cpp_block)
    return cpp_block


def is_operator_function(element_c: CppElementAndComment) -> bool:
    assert element_c.tag() in ["function", "function_decl"]
    type_attr = element_c.attribute_value("type")
    if type_attr is None:
        return False
    else:
        return type_attr == "operator"


def _shall_publish_function(function_c: CppElementAndComment, options: SrcmlOptions) -> bool:
    if len(options.functions_api_prefixes) == 0:
        return True
    for child_fn in function_c.srcml_xml:
        child_fn_tag = srcml_utils.clean_tag_or_attrib(child_fn.tag)
        if child_fn_tag == "type":
            for child_type in child_fn:
                child_type_tag = srcml_utils.clean_tag_or_attrib(child_type.tag)
                if child_type_tag == "name":
                    typename = child_type.text
                    if typename in options.functions_api_prefixes:
                        return True
    return False


def _shall_publish(cpp_element: CppElementAndComment, options: SrcmlOptions) -> bool:
    tag = cpp_element.tag()
    if tag in ["function", "function_decl"]:
        return _shall_publish_function(cpp_element, options)
    elif tag in ["namespace", "enum", "struct", "class"]:
        if len(options.api_suffixes) == 0:
            return True

        comment = cpp_element.cpp_element_comments.comment_end_of_line + cpp_element.cpp_element_comments.comment()
        for comment_child in srcml_utils.children_with_tag(cpp_element.srcml_xml, "comment"):
            if comment_child.text is not None:
                comment += comment_child.text

        for api_suffix in options.api_suffixes:
            if api_suffix in comment:
                return True
        return False
    else:
        return True


def shall_ignore_comment(cpp_comment: CppComment, last_ignored_child: Optional[CppElementAndComment]) -> bool:
    ignore_comment = False
    if last_ignored_child is not None:
        last_ignore_child_end = last_ignored_child.end()

        comment_start = cpp_comment.start()
        last_ignore_child_end = last_ignored_child.end()
        if (
            comment_start is not None
            and last_ignore_child_end is not None
            and comment_start.line == last_ignore_child_end.line
        ):
            # When there is an explanation following a typedef or a struct forward decl,
            # we keep both the code (as a comment) and its comment
            if last_ignored_child.tag() in ["typedef", "struct_decl"]:
                cpp_comment.comment = "// " + last_ignored_child.str_code_verbatim() + "    " + cpp_comment.comment
                ignore_comment = False
            else:
                ignore_comment = True
    return ignore_comment


def fill_block(options: SrcmlOptions, element: SrcmlXmlWrapper, inout_block_content: CppBlock) -> None:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """

    last_ignored_child: Optional[CppElementAndComment] = None

    children: List[CppElementAndComment] = srcml_comments.get_children_with_comments(element)
    for _i, child_c in enumerate(children):
        if not _shall_publish(child_c, options):
            continue

        child_tag = child_c.tag()
        child_name = child_c.name_code()

        try:
            if child_tag == "decl_stmt":
                inout_block_content.block_children.append(parse_decl_stmt(options, child_c))
            elif child_tag == "decl":
                cpp_decl = parse_decl(options, child_c, None)
                inout_block_content.block_children.append(cpp_decl)
            elif child_tag == "function_decl":
                if is_operator_function(child_c):
                    child_c.emit_warning("Operator functions are ignored")
                    inout_block_content.block_children.append(parse_unprocessed(options, child_c))
                else:
                    assert child_name is not None
                    inout_block_content.block_children.append(parse_function_decl(options, child_c))
            elif child_tag == "function":
                assert child_name is not None
                if is_operator_function(child_c):
                    child_c.emit_warning("Operator functions are ignored")
                    inout_block_content.block_children.append(parse_unprocessed(options, child_c))
                else:
                    inout_block_content.block_children.append(parse_function(options, child_c))

            elif child_tag == "constructor_decl":
                inout_block_content.block_children.append(parse_constructor_decl(options, child_c))
            elif child_tag == "constructor":
                inout_block_content.block_children.append(parse_constructor(options, child_c))

            elif child_tag == "comment":
                cpp_comment = parse_comment(options, child_c)

                if srcml_comments.EMPTY_LINE_COMMENT_CONTENT in cpp_comment.comment:
                    inout_block_content.block_children.append(CppEmptyLine(child_c))
                else:
                    if not shall_ignore_comment(cpp_comment, last_ignored_child):
                        inout_block_content.block_children.append(cpp_comment)

            elif child_tag == "struct" or child_tag == "class":
                assert child_name is not None
                inout_block_content.block_children.append(parse_struct_or_class(options, child_c))
            elif child_tag == "namespace":
                inout_block_content.block_children.append(parse_namespace(options, child_c))
            elif child_tag == "enum":
                inout_block_content.block_children.append(parse_enum(options, child_c))
            elif child_tag == "block_content":
                inout_block_content.block_children.append(parse_block_content(options, child_c))
            elif child_tag in ["public", "protected", "private"]:
                inout_block_content.block_children.append(parse_public_protected_private(options, child_c))
            else:
                last_ignored_child = child_c
                inout_block_content.block_children.append(parse_unprocessed(options, child_c))
        except SrcMlExceptionDetailed as e:
            emit_warning_if_not_quiet(options, f'A cpp element of type "{child_tag}" was ignored. Details follow\n{e}')


def parse_unit(options: SrcmlOptions, element: SrcmlXmlWrapper) -> CppUnit:
    assert element.tag() == "unit"
    cpp_unit = CppUnit(element)
    fill_block(options, element, cpp_unit)
    cpp_unit.fill_children_parents()
    return cpp_unit


def parse_block_content(
    options: SrcmlOptions, element_c: CppElementAndComment
):  # element: SrcmlXmlWrapper) -> CppBlockContent:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """
    assert element_c.tag() == "block_content"

    block_content = CppBlockContent(element_c)
    fill_block(options, element_c, block_content)
    return block_content


def parse_comment(options: SrcmlOptions, element_c: CppElementAndComment) -> CppComment:
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    """
    assert element_c.tag() == "comment"
    assert len(element_c.srcml_xml) == 0  # a comment has no child

    result = CppComment(element_c, element_c.cpp_element_comments)

    comment = code_utils.str_none_empty(element_c.text())
    lines = comment.split("\n")
    if len(lines) > 1:
        lines = list(map(lambda line: "" if "_SRCML_EMPTY_LINE_" in line else line, lines))
        comment = "\n".join(lines)
        result.comment = comment
    else:
        result.comment = comment

    return result


def parse_namespace(options: SrcmlOptions, element_c: CppElementAndComment) -> CppNamespace:
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    assert element_c.tag() == "namespace"
    result = CppNamespace(element_c, element_c.cpp_element_comments)
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.ns_name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


def parse_enum(options: SrcmlOptions, element_c: CppElementAndComment) -> CppEnum:
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """
    assert element_c.tag() == "enum"
    result = CppEnum(element_c, element_c.cpp_element_comments)

    if "type" in element_c.srcml_xml.attrib.keys():
        enum_type = element_c.attribute_value("type")
        assert enum_type is not None
        result.enum_type = enum_type

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.enum_name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result
