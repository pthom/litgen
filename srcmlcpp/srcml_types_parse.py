import copy

from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_caller, srcml_utils, srcml_warnings, srcml_main, srcml_comments
from srcmlcpp.srcml_warnings import SrcMlExceptionDetailed
from srcmlcpp.srcml_options import SrcmlOptions


def parse_unprocessed(options: SrcmlOptions, element_c: CppElementAndComment) -> CppUnit:
    result = CppUnprocessed(element_c.srcml_element, element_c.cpp_element_comments)
    result.code = srcml_caller.srcml_to_code(element_c.srcml_element)
    return result


def parse_type(options: SrcmlOptions, element: ET.Element, previous_decl: CppDecl) -> CppType:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """

    def recompose_type_name(element: ET.Element) -> str:
        is_composed_type = (element.text is None)
        return srcml_caller.srcml_to_code(element).strip() if is_composed_type else element.text

    assert srcml_utils.clean_tag_or_attrib(element.tag) == "type"
    result = CppType(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            typename = recompose_type_name(child)
            result.names.append(typename)
        elif child_tag == "specifier":
            result.specifiers.append(child.text)
        elif child_tag == "modifier":
            modifier = child.text
            if modifier not in CppType.authorized_modifiers():
                raise SrcMlExceptionDetailed(child, f'modifier "{modifier}" is not authorized', options)
            result.modifiers.append(child.text)
        elif child_tag == "argument_list":
            result.argument_list.append(child.text)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    if len(result.names) == 0 and "..." not in result.modifiers:
        if previous_decl is None:
            raise SrcMlExceptionDetailed(result, "Can't find type name", options)
        assert previous_decl is not None
        result.names = previous_decl.cpp_type.names

    if len(result.names) == 0 and "..." not in result.modifiers:
        raise SrcMlExceptionDetailed(result, "len(result.names) == 0!", options)

    # process api names
    for name in result.names:
        is_api_name = False
        for api_prefix in options.functions_api_prefixes:
            if name.startswith(api_prefix):
                is_api_name = True
        if is_api_name:
            result.names.remove(name)
            result.specifiers = [name] + result.specifiers

    return result


def _parse_init_expr(element: ET.Element) -> str:
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
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "init"
    expr = srcml_utils.child_with_tag(element, "expr")

    # Case for simple literals
    if len(expr) == 1:
        for child in expr:
            if srcml_utils.clean_tag_or_attrib(child.tag) in ["literal", "name"]:
                if child.text is not None:
                    r = child.text
                    return r

    # More complex cases
    r = srcml_caller.srcml_to_code(expr)
    return r


def _parse_name(element: ET.Element) -> str:
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "name"
    is_composed = (element.text is None)
    name = srcml_caller.srcml_to_code(element).strip() if is_composed else element.text
    return name


def parse_decl_from_code(options: SrcmlOptions, code: str, previous_decl: CppDecl) -> CppDecl:
    cpp_unit = srcml_main.code_to_cpp_unit(options, code)
    assert len(cpp_unit.block_children) == 1
    assert cpp_unit.block_children[0].tag() == "decl"
    return cpp_unit.block_children[0]


def parse_decl(options: SrcmlOptions, element_c: CppElementAndComment, previous_decl: CppDecl) -> CppDecl:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    assert element_c.tag() == "decl"
    result = CppDecl(element_c.srcml_element, element_c.cpp_element_comments)
    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "type":
            result.cpp_type = parse_type(options, child, previous_decl)
        elif child_tag == "name":
            result.name = _parse_name(child)
        elif child_tag == "init":
            result.init = _parse_init_expr(child)
        elif child_tag == "range":
            pass # this is for C bit fields
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_decl_stmt(options: SrcmlOptions, element_c: CppElementAndComment) -> CppDeclStatement:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#variable-declaration-statement
    https://www.srcmlcpp.org/doc/cpp_srcML.html#variable-declaration
    """
    assert element_c.tag() == "decl_stmt"

    previous_decl: CppDecl = None
    result = CppDeclStatement(element_c.srcml_element, element_c.cpp_element_comments)
    for child in element_c.srcml_element:
        child_c = copy.deepcopy(element_c); child_c.srcml_element = child
        if child_c.tag() == "decl":
            cpp_decl = parse_decl(options, child_c, previous_decl)
            result.cpp_decls.append(cpp_decl)
            previous_decl = cpp_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_c.tag()}", options)

    # the comments were copied to all the internal decls, we can remove them from the decl_stmt
    result.cpp_element_comments = CppElementComments()

    return result


def parse_parameter(options: SrcmlOptions, element: ET.Element) -> CppParameter:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#function-declaration
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "parameter"
    result = CppParameter(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "decl":
            child_c = CppElementAndComment(child, CppElementComments())
            result.decl = parse_decl(options, child_c, None)
        elif child_tag == "type":
            result.template_type = parse_type(options, child, None) # This is only for template parameters
        elif child_tag == "name":
            result.template_name = child.text # This is only for template parameters
        elif child_tag == "function_decl":
            raise SrcMlExceptionDetailed(
                child, f"A function uses a function_decl as a param. It was discarded", options)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_parameter_list(options: SrcmlOptions, element: ET.Element) -> CppParameterList:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#function-declaration
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "parameter_list"
    result = CppParameterList(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "parameter":
            result.parameters.append(parse_parameter(options, child))
        else:
            raise SrcMlExceptionDetailed(child, result)
    return result


def parse_template(options: SrcmlOptions, element: ET.Element) -> CppTemplate:
    """
    Template parameters of a function, struct or class
    https://www.srcmlcpp.org/doc/cpp_srcML.html#template
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "template"
    result = CppTemplate(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "parameter_list":
            result.parameter_list = parse_parameter_list(options, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)
    return result


def fill_function_decl(options: SrcmlOptions, element_c: CppElementAndComment, function_decl: CppFunctionDecl):
    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "type":
            if function_decl.type is None or len(function_decl.type.names) == 0:
                parsed_type = parse_type(options, child, None)
                function_decl.type = parsed_type
            else:
                additional_type = parse_type(options, child, None)
                function_decl.type.names += additional_type.names
        elif child_tag == "name":
            function_decl.name = _parse_name(child)
        elif child_tag == "parameter_list":
            function_decl.parameter_list = parse_parameter_list(options, child)
        elif child_tag == "specifier":
            function_decl.specifiers.append(child.text)
        elif child_tag == "attribute":
            pass # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag == "template":
            function_decl.template = parse_template(options, child)
        elif child_tag == "block":
            pass # will be handled by parse_function
        elif child_tag == "modifier":
            raise SrcMlExceptionDetailed(child, "C style function pointers are poorly supported", options)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    if len(function_decl.type.names) >= 2 and function_decl.type.names[0] == "auto":
        function_decl.type.names = function_decl.type.names[1 : ]


def parse_function_decl(options: SrcmlOptions, element_c: CppElementAndComment) -> CppFunctionDecl:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#function-declaration
    """
    assert element_c.tag() == "function_decl"
    result = CppFunctionDecl(element_c.srcml_element, element_c.cpp_element_comments)
    fill_function_decl(options, element_c, result)
    return result


def parse_function(options: SrcmlOptions, element_c: CppElementAndComment) -> CppFunction:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() == "function"
    result = CppFunction(element_c.srcml_element, element_c.cpp_element_comments)
    fill_function_decl(options, element_c, result)

    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "block":
            child_c = CppElementAndComment(child, CppElementComments())
            result.block = parse_unprocessed(options, child_c)
        elif child_tag in ["type", "name", "parameter_list", "specifier", "attribute", "template"]:
            pass # already handled by fill_function_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)
    return result


###############################################

def fill_constructor_decl(options: SrcmlOptions, element_c: CppElementAndComment, constructor_decl: CppConstructorDecl):
    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            constructor_decl.name = _parse_name(child)
        elif child_tag == "parameter_list":
            constructor_decl.parameter_list = parse_parameter_list(options, child)
        elif child_tag == "specifier":
            constructor_decl.specifiers.append(child.text)
        elif child_tag == "attribute":
            pass # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag in ["block", "member_init_list"]:
            pass # will be handled by parse_constructor
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)


def parse_constructor_decl(options: SrcmlOptions, element_c: CppElementAndComment) -> CppConstructorDecl:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#constructor-declaration
    """
    assert element_c.tag() == "constructor_decl"
    result = CppConstructorDecl(element_c.srcml_element, element_c.cpp_element_comments)
    fill_constructor_decl(options, element_c, result)
    return result


def parse_constructor(options: SrcmlOptions, element_c: CppElementAndComment) -> CppConstructor:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() == "constructor"
    result = CppConstructor(element_c.srcml_element, element_c.cpp_element_comments)
    fill_constructor_decl(options, element_c, result)

    for child in element_c.srcml_element:
        child_c = CppElementAndComment(child, CppElementComments())
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "block":
            result.block = parse_unprocessed(options, child_c)
        elif child_tag == "member_init_list":
            result.member_init_list = parse_unprocessed(options, child_c)
        elif child_tag in ["name", "parameter_list", "specifier", "attribute"]:
            pass # alread handled by fill_constructor_decl
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_super(options: SrcmlOptions, element: ET.Element) -> CppSuper:
    """
    Define a super classes of a struct or class
    https://www.srcmlcpp.org/doc/cpp_srcML.html#struct-definition
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "super"
    result = CppSuper(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "specifier":
            result.specifier = child.text
        elif child_tag == "name":
            result.name = _parse_name(child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_super_list(options: SrcmlOptions, element: ET.Element) -> CppSuperList:
    """
    Define a list of super classes of a struct or class
    https://www.srcmlcpp.org/doc/cpp_srcML.html#struct-definition
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "super_list"
    result = CppSuperList(element)
    for child in element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "super":
            result.super_list.append(parse_super(options, child))
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_struct_or_class(options: SrcmlOptions, element_c: CppElementAndComment) -> CppStruct:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#struct-definition
    https://www.srcmlcpp.org/doc/cpp_srcML.html#class-definition
    """
    element_tag = element_c.tag()
    assert element_tag in ["struct", "class"]
    if element_tag == "struct":
        result = CppStruct(element_c.srcml_element, element_c.cpp_element_comments)
    else:
        result = CppClass(element_c.srcml_element, element_c.cpp_element_comments)

    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = _parse_name(child)
        elif child_tag == "super_list":
            result.super_list = parse_super_list(options, child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        elif child_tag == "template":
            result.template = parse_template(options, child)
        elif child_tag == "comment":
            comment_text = code_utils.cpp_comment_remove_comment_markers(child.text)
            if len(result.cpp_element_comments.comment_end_of_line) > 0:
                result.cpp_element_comments.comment_end_of_line += " - "
            result.cpp_element_comments.comment_end_of_line += comment_text
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_public_protected_private(options: SrcmlOptions, element_c: CppElementAndComment) -> CppPublicProtectedPrivate:
    """
    See https://www.srcmlcpp.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types
    """
    access_type = element_c.tag()
    assert access_type in ["public", "protected", "private"]
    type = element_c.attribute_value("type")

    block_content = CppPublicProtectedPrivate(element_c.srcml_element, access_type, type)
    fill_block(options, element_c.srcml_element, block_content)
    return block_content


def parse_block(options: SrcmlOptions, element: ET.Element) -> CppBlock:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#block
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "block"

    cpp_block = CppBlock(element)
    fill_block(options, element, cpp_block)
    return cpp_block


def is_operator_function(element_c: CppElementAndComment) -> bool:
    assert element_c.tag() in ["function", "function_decl"]
    return element_c.attribute_value("type") == "operator"


def _shall_publish_function(function_c: CppElementAndComment, options: SrcmlOptions):
    if len(options.functions_api_prefixes) == 0:
        return True
    for child_fn in function_c.srcml_element:
        child_fn_tag = srcml_utils.clean_tag_or_attrib(child_fn.tag)
        if child_fn_tag == "type":
            for child_type in child_fn:
                child_type_tag = srcml_utils.clean_tag_or_attrib(child_type.tag)
                if child_type_tag == "name":
                    typename = child_type.text
                    if typename in options.functions_api_prefixes:
                        return True
    return False


def _shall_publish(cpp_element: CppElementAndComment, options: SrcmlOptions):
    tag = cpp_element.tag()
    if tag in ["function", "function_decl"]:
        return _shall_publish_function(cpp_element, options)
    elif tag in ["namespace", "enum", "struct", "class"]:
        if len(options.api_suffixes) == 0:
            return True

        comment = cpp_element.cpp_element_comments.comment_end_of_line + cpp_element.cpp_element_comments.comment()
        for comment_child in srcml_utils.children_with_tag(cpp_element.srcml_element, "comment"):
            if comment_child.text is not None:
                comment += comment_child.text

        for api_suffix in options.api_suffixes:
            if api_suffix in comment:
                return True
        return False
    else:
        return True


def fill_block(options: SrcmlOptions, element: ET.Element, inout_block_content: CppBlock):
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#block_content
    """

    last_ignored_child: CppElementAndComment = None

    children = srcml_main.get_children_with_comments(options, element)
    for i, child_c in enumerate(children):
        if not _shall_publish(child_c, options):
            continue

        child_tag = child_c.tag()

        try:
            if child_tag == "decl_stmt":
                inout_block_content.block_children.append(parse_decl_stmt(options, child_c))
            elif child_tag == "decl":
                inout_block_content.block_children.append(parse_decl(options, child_c, None))
            elif child_tag == "function_decl":
                if is_operator_function(child_c):
                    srcml_warnings.emit_srcml_warning(child_c, "Operator functions are ignored", options)
                    inout_block_content.block_children.append(parse_unprocessed(options, child_c))
                else:
                    inout_block_content.block_children.append(parse_function_decl(options, child_c))
            elif child_tag == "function":
                if is_operator_function(child_c):
                    srcml_warnings.emit_srcml_warning(child_c.srcml_element, "Operator functions are ignored", options)
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
                    inout_block_content.block_children.append(CppEmptyLine(child_c.srcml_element))
                else:
                    ignore_comment = False
                    if last_ignored_child is not None:
                        last_ignore_child_end_position = last_ignored_child.end()
                        if cpp_comment.start().line == last_ignore_child_end_position.line:
                            # When there is an explanation following a typedef or a struct forward decl,
                            # we keep both the code (as a comment) and its comment
                            if last_ignored_child.tag() in ["typedef", "struct_decl"]:
                                cpp_comment.set_text("// " + last_ignored_child.str_code_verbatim() + "    " + cpp_comment.text())
                                ignore_comment = False
                            else:
                                ignore_comment = True

                    if not ignore_comment:
                        inout_block_content.block_children.append(cpp_comment)

            elif child_tag == "struct":
                inout_block_content.block_children.append(parse_struct_or_class(options, child_c))
            elif child_tag == "class":
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
            srcml_warnings.emit_warning(
                f'A cpp element of type "{child_tag}" was ignored. Details follow\n {e}', options)


def parse_unit(options: SrcmlOptions, element: ET.Element) -> CppUnit:
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "unit"
    cpp_unit = CppUnit(element)
    fill_block(options, element, cpp_unit)
    return cpp_unit


def parse_block_content(options: SrcmlOptions, element: ET.Element) -> CppBlockContent:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#block_content
    """
    assert srcml_utils.clean_tag_or_attrib(element.tag) == "block_content"

    block_content = CppBlockContent(element)
    fill_block(element, block_content)
    return block_content


def parse_comment(options: SrcmlOptions, element_c: CppElementAndComment) -> CppComment:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#comment
    """
    assert element_c.tag() == "comment"
    assert len(element_c.srcml_element) == 0 # a comment has no child

    result = CppComment(element_c.srcml_element, element_c.cpp_element_comments)
    result.comment = element_c.text()
    return result


def parse_namespace(options: SrcmlOptions, element_c: CppElementAndComment) -> CppNamespace:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#namespace
    """
    assert element_c.tag() == "namespace"
    result = CppNamespace(element_c.srcml_element, element_c.cpp_element_comments)
    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result


def parse_enum(options: SrcmlOptions, element_c: CppElementAndComment) -> CppEnum:
    """
    https://www.srcmlcpp.org/doc/cpp_srcML.html#enum-definition
    https://www.srcmlcpp.org/doc/cpp_srcML.html#enum-class
    """
    assert element_c.tag() == "enum"
    result = CppEnum(element_c.srcml_element, element_c.cpp_element_comments)

    if "type" in element_c.srcml_element.attrib.keys():
        result.type = element_c.attribute_value("type")

    for child in element_c.srcml_element:
        child_tag = srcml_utils.clean_tag_or_attrib(child.tag)
        if child_tag == "name":
            result.name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child)
        else:
            raise SrcMlExceptionDetailed(child, f"unhandled tag {child_tag}", options)

    return result
