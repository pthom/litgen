"""
This is the heart of the parsing of a xml tree into a tree of Cpp Elements (defined in srcml_types).

The main interface of this module is:
    parse_unit(options: SrcmlcppOptions, element: SrcmlWrapper) -> CppUnit

All the other functions can be considered private to this module.
"""
from __future__ import annotations
from typing import Optional
from xml.etree import ElementTree as ET

import srcmlcpp.internal.code_to_srcml
from codemanip import code_utils
from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp import SrcmlWrapper
from srcmlcpp.scrml_warning_settings import WarningType
from srcmlcpp.cpp_types import (
    CppElementAndComment,
    CppElementComments,
    CppUnit,
    CppBlock,
    CppBlockContent,
    CppComment,
    CppAccessType,
    CppClass,
    CppConditionMacro,
    CppConstructorDecl,
    CppConstructor,
    CppDeclStatement,
    CppDecl,
    CppDefine,
    CppEmptyLine,
    CppEnum,
    CppFunctionDecl,
    CppFunction,
    CppNamespace,
    CppParameterList,
    CppParameter,
    CppPublicProtectedPrivate,
    CppStruct,
    CppSuperList,
    CppSuper,
    CppTemplate,
    CppType,
    CppUnprocessed,
)
from srcmlcpp.internal import code_to_srcml, srcml_comments, srcml_utils, fix_brace_init_default_value
from srcmlcpp.internal.srcmlcpp_exception_detailed import (
    SrcmlcppExceptionDetailed,
)
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


_PROGRESS_BAR_TITLE_SRCML_PARSE = "srcmlcpp: Create CppElements................. "


def parse_unprocessed(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppUnprocessed:  # noqa
    result = CppUnprocessed(element_c, element_c.cpp_element_comments)
    result.parent = parent
    return result


def parse_type(
    options: SrcmlcppOptions,
    element: SrcmlWrapper,
    parent: CppElementAndComment,
    previous_decl: Optional[CppDecl],
    is_operator_return_type: bool = False,
) -> CppType:
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

    def recompose_type_name(element: SrcmlWrapper) -> str:
        element_text = element.text()
        if element_text is None:
            # case for composed type
            return element.str_code_verbatim().strip()
        else:
            return element_text

    assert element.tag() == "type"
    result = CppType(element)
    result.parent = parent
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
                raise SrcmlcppExceptionDetailed(child, f'modifier "{modifier_text}" is not authorized')
            result.modifiers.append(modifier_text)
        # elif child_tag == "argument_list":
        #     result.argument_list.append(child.text)
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    if not is_operator_return_type:
        # C++ cast operator will not be parsed as having a return type (since the type is actually the function name!)
        if len(result.typenames) == 0 and "..." not in result.modifiers and "auto" not in result.specifiers:
            if previous_decl is None:
                raise SrcmlcppExceptionDetailed(result, "Can't find type name")
            assert previous_decl is not None
            result.typenames = previous_decl.cpp_type.typenames

        if len(result.typenames) == 0 and "..." not in result.modifiers and "auto" not in result.specifiers:
            raise SrcmlcppExceptionDetailed(result, "len(result.names) == 0!")

    # process api names
    for name in result.typenames:
        is_api_name = False
        for api_prefix in options.functions_api_prefixes_list():
            if name.startswith(api_prefix):
                is_api_name = True
        if is_api_name:
            result.typenames.remove(name)
            result.specifiers = [name] + result.specifiers

    return result


def _parse_expr(element: SrcmlWrapper) -> str:
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

    assert element.tag() == "expr"
    expr = element
    eval_literal_value = expr_literal_value(expr.srcml_xml)
    if eval_literal_value is not None:
        r = eval_literal_value
    else:
        r = code_to_srcml.srcml_to_code(expr.srcml_xml)

    return r


def _parse_init_expr(element: SrcmlWrapper) -> str:
    assert element.tag() == "init"

    expr = element.wrapped_child_with_tag("expr")
    if expr is not None:
        r = _parse_expr(expr)
    else:
        r = element.str_code_verbatim().strip()
        if r.startswith("="):
            r = r[1:]

    return r


def _parse_name(element: SrcmlWrapper) -> str:
    assert element.tag() == "name"
    element_text = element.text()
    if element_text is None:
        # composed name
        name = element.str_code_verbatim().strip()
    else:
        name = element_text.strip()
    return name


def parse_condition_macro(
    _options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppConditionMacro:
    # accept only #if, #ifdef, #ifndef, #endif, #else, #elif
    assert element_c.tag() in ["if", "ifdef", "ifndef", "endif", "else", "elif"]
    result = CppConditionMacro(element_c, element_c.cpp_element_comments)
    result.parent = parent
    macro_code = srcmlcpp.internal.code_to_srcml.srcml_to_code(element_c.srcml_xml)
    result.macro_code = macro_code
    return result


def parse_define(options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment) -> CppDefine:
    """
    https://www.srcml.org/doc/cpp_srcML.html##define

    srcmlcpp xml "#define MY_ANSWER(x) (x+ 1)"

        <?xml version="1.0" ?>
        <unit xmlns="http://www.srcML.org/srcML/src" xmlns:ns1="http://www.srcML.org/srcML/cpp" revision="1.0.0" language="C++">
           <ns1:define>
              #
              <ns1:directive>define</ns1:directive>

              <ns1:macro>
                 <name>MY_ANSWER</name>
                 <parameter_list>
                    (
                    <parameter>
                       <type>
                          <name>x</name>
                       </type>
                    </parameter>
                    )
                 </parameter_list>
              </ns1:macro>
              <ns1:value>(x+ 1)</ns1:value>
           </ns1:define>
        </unit>
    """
    assert element_c.tag() == "define"
    result = CppDefine(element_c, element_c.cpp_element_comments)
    result.parent = parent

    def parse_inner_macro(macro_element: SrcmlWrapper) -> None:
        for macro_child in macro_element.make_wrapped_children():
            macro_child_tag = macro_child.tag()
            if macro_child_tag == "name":
                text = macro_child.text()
                if text is not None:
                    result.macro_name = text
            elif macro_child_tag == "parameter_list":
                result.macro_parameters_str = macro_child.str_code_verbatim()

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "directive":
            continue
        elif child_tag == "macro":
            parse_inner_macro(child)
        elif child_tag == "value":
            text = child.text()
            if text is not None:
                result.macro_value = text
    return result


def _parse_decl_initializer_list(_options: SrcmlcppOptions, element_c: SrcmlWrapper) -> str:
    assert element_c.tag() == "argument_list"
    arguments = element_c.wrapped_children_with_tag("argument")
    arguments_values = []
    for argument in arguments:
        expr = argument.wrapped_child_with_tag("expr")
        if expr is None:
            element_c.raise_exception("parse_decl: initializer list with with unparsable expr")
        else:
            expr_value = _parse_expr(expr)
            arguments_values.append(expr_value)

    if len(arguments_values) == 0:
        return "{}"
    else:
        r = "{" + ", ".join(arguments_values) + "}"
        return r


def parse_decl(
    options: SrcmlcppOptions,
    element_c: CppElementAndComment,
    parent: CppElementAndComment,
    previous_decl: Optional[CppDecl],
) -> CppDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    assert element_c.tag() == "decl"
    result = CppDecl(element_c, element_c.cpp_element_comments)
    result.parent = parent
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "type":
            result.cpp_type = parse_type(options, child, element_c, previous_decl)
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
        elif child_tag == "argument_list":
            # initializer list
            result.initial_value_via_initializer_list = True
            result.initial_value_code = _parse_decl_initializer_list(options, child)
        elif child_tag == "range":
            # this is for C bit fields
            result.bitfield_range = child.str_code_verbatim()
        else:
            raise SrcmlcppExceptionDetailed(child, f"parse_decl: unhandled tag {child_tag}")

    return result


def parse_decl_stmt(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppDeclStatement:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """
    assert element_c.tag() == "decl_stmt"

    previous_decl: Optional[CppDecl] = None
    result = CppDeclStatement(element_c, element_c.cpp_element_comments)
    result.parent = parent
    for child in element_c.make_wrapped_children():
        child_c = element_c
        child_c.srcml_xml = child.srcml_xml
        if child_c.tag() == "decl":
            child_name = child_c.extract_name_from_xml()
            if child_name is None:
                raise SrcmlcppExceptionDetailed(child, "Encountered decl without name!")
            cpp_decl = parse_decl(options, child_c, result, previous_decl)
            result.cpp_decls.append(cpp_decl)
            previous_decl = cpp_decl
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_c.tag()}")

    # the comments were copied to all the internal decls, we can remove them from the decl_stmt
    result.cpp_element_comments = CppElementComments()

    return result


def parse_parameter(options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment) -> CppParameter:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element.tag() == "parameter"
    result = CppParameter(element)
    result.parent = parent
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "decl":
            child_c = CppElementAndComment(child, CppElementComments())
            result.decl = parse_decl(options, child_c, result, None)
        elif child_tag == "type":
            # This is not the parameter's type, this is a template parameter which will be either "class" or "typename"
            # as in template<typename T> or template<class T>
            assert child.has_xml_name()
            template_type = child.extract_name_from_xml()
            assert template_type is not None
            result.template_type = template_type
        elif child_tag == "name":
            child_text = child.text()
            assert child_text is not None
            result.template_name = child_text  # This is only for template parameters
        elif child_tag == "init":
            # This is only for int template parameters e.g. `template<int N=1> void f()`
            result.template_init = _parse_init_expr(child)
        elif child_tag == "function_decl":
            raise SrcmlcppExceptionDetailed(child, "Can't use a function_decl as a param.")
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_parameter_list(
    options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment
) -> CppParameterList:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element.tag() == "parameter_list"
    result = CppParameterList(element)
    result.parent = parent
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "parameter":
            result.parameters.append(parse_parameter(options, child, result))
        elif child_tag == "comment":
            pass
        else:
            element.emit_warning(f"parse_parameter_list unhandled tag {child_tag}")
    return result


def parse_template(options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment) -> CppTemplate:
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """
    assert element.tag() == "template"
    result = CppTemplate(element)
    result.parent = parent
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "parameter_list":
            result.parameter_list = parse_parameter_list(options, child, result)
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


def fill_function_decl(
    options: SrcmlcppOptions,
    element_c: CppElementAndComment,
    function_decl: CppFunctionDecl,
) -> None:
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "type":
            if not hasattr(function_decl, "return_type") or len(function_decl.return_type.typenames) == 0:
                parsed_type = parse_type(
                    options, child, function_decl, None, is_operator_return_type=is_operator_function(element_c)
                )
                function_decl.return_type = parsed_type
            else:
                additional_type = parse_type(options, child, function_decl.return_type, None)
                function_decl.return_type.typenames += additional_type.typenames
        elif child_tag == "name":
            function_decl.function_name = _parse_name(child)
            if function_decl.function_name == "operator":
                # For operator functions, the name is given in two parts:
                #
                # <ns0:name ns1:start="6:16" ns1:end="6:24">
                #     operator
                #     <ns0:name ns1:start="6:24" ns1:end="6:24">+</ns0:name>
                # </ns0:name>
                #
                sub_names = child.wrapped_children_with_tag("name")
                assert len(sub_names) == 1
                operator_name = _parse_name(sub_names[0])
                if len(operator_name) > 0 and (operator_name[0].isalpha() or operator_name[0] == "_"):
                    function_decl.function_name += " "
                function_decl.function_name += operator_name
        elif child_tag == "parameter_list":
            function_decl.parameter_list = parse_parameter_list(options, child, function_decl)
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            function_decl.specifiers.append(child_text)
        elif child_tag == "attribute":
            pass  # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag == "template":
            function_decl.template = parse_template(options, child, function_decl)
        elif child_tag == "block":
            pass  # will be handled by parse_function
        elif child_tag == "modifier":
            raise SrcmlcppExceptionDetailed(child, "C style function pointers are poorly supported")
        elif child_tag == "comment":
            child_text = child.text()
            if child_text is not None:
                function_decl.cpp_element_comments.add_eol_comment(child_text)
        elif child_tag == "literal":
            # pure virtual function
            child_text = child.text()
            if child_text is None:
                raise SrcmlcppExceptionDetailed(
                    child, f"unhandled literal {child_tag} (was expecting '=0' for a pure virtual function"
                )
            assert child_text is not None
            if child_text.strip() != "0":
                raise SrcmlcppExceptionDetailed(
                    child, f"unhandled literal {child_tag} (was expecting '=0' for a pure virtual function"
                )
            function_decl.is_pure_virtual = True
        elif child_tag == "noexcept":
            arg_list = child.wrapped_child_with_tag("argument_list")
            if arg_list is None:
                function_decl._noexcept = ""
            else:
                function_decl._noexcept = arg_list.str_code_verbatim()
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")


def parse_function_decl(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppFunctionDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert element_c.tag() in ["function_decl", "destructor_decl"]
    result = CppFunctionDecl(element_c, element_c.cpp_element_comments)
    result.parent = parent
    fill_function_decl(options, element_c, result)
    return result


def parse_function(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppFunction:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() in ["function", "destructor"]
    result = CppFunction(element_c, element_c.cpp_element_comments)
    result.parent = parent
    fill_function_decl(options, element_c, result)

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "block":
            child_c = CppElementAndComment(child, CppElementComments())
            result.block = parse_unprocessed(options, child_c, result)
        elif child_tag in [
            "type",
            "name",
            "parameter_list",
            "specifier",
            "attribute",
            "template",
            "comment",
            "noexcept",
        ]:
            pass  # already handled by fill_function_decl
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


###############################################


def fill_constructor_decl(
    options: SrcmlcppOptions,
    element_c: CppElementAndComment,
    constructor_decl: CppConstructorDecl,
) -> None:
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            constructor_decl.function_name = _parse_name(child)
        elif child_tag == "parameter_list":
            constructor_decl.parameter_list = parse_parameter_list(options, child, constructor_decl)
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            constructor_decl.specifiers.append(child_text)
        elif child_tag == "comment":
            child_text = child.text()
            if child_text is not None:
                constructor_decl.cpp_element_comments.comment_end_of_line += " " + child_text
        elif child_tag == "attribute":
            pass  # compiler options, such as [[gnu::optimize(0)]]
        elif child_tag in ["block", "member_init_list"]:
            pass  # will be handled by parse_constructor
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")


def parse_constructor_decl(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppConstructorDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """
    assert element_c.tag() == "constructor_decl"
    result = CppConstructorDecl(element_c, element_c.cpp_element_comments)
    result.parent = parent
    fill_constructor_decl(options, element_c, result)
    return result


def parse_constructor(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppConstructor:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    assert element_c.tag() == "constructor"
    result = CppConstructor(element_c, element_c.cpp_element_comments)
    result.parent = parent
    fill_constructor_decl(options, element_c, result)

    for child in element_c.make_wrapped_children():
        child_c = CppElementAndComment(child, CppElementComments())
        child_tag = child.tag()
        if child_tag == "block":
            result.block = parse_unprocessed(options, child_c, result)
        elif child_tag == "member_init_list":
            result.member_init_list = parse_unprocessed(options, child_c, result)
        elif child_tag in ["name", "parameter_list", "specifier", "attribute"]:
            pass  # alread handled by fill_constructor_decl
        elif child_tag == "comment":
            pass
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_super(options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment) -> CppSuper:
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert element.tag() == "super"
    result = CppSuper(element)
    result.parent = parent
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            result.specifier = child_text
        elif child_tag == "name":
            result.superclass_name = _parse_name(child)
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_super_list(options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment) -> CppSuperList:
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    assert element.tag() == "super_list"
    result = CppSuperList(element)
    result.parent = parent
    for child in element.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "super":
            result.super_list.append(parse_super(options, child, result))
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def _add_comment_child_before_block(element_c: CppElementAndComment, child: SrcmlWrapper) -> None:
    """
    For struct, enum and namespace, we might add a comment like this:
        struct Foo
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


def parse_struct_or_class(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppStruct:
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
    result.parent = parent

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.class_name = _parse_name(child)
        elif child_tag == "super_list":
            result.super_list = parse_super_list(options, child, result)
        elif child_tag == "block":
            result.block = parse_block(options, child, result)
        elif child_tag == "template":
            result.template = parse_template(options, child, result)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        elif child_tag == "decl":
            raise SrcmlcppExceptionDetailed(child, "Skipped struct because it misses a ';' at the end")
        elif child_tag == "specifier":
            child_text = child.text()
            assert child_text is not None
            result.specifier = child_text
        elif child_tag == "macro":
            macro_name = child.extract_name_from_xml()
            assert macro_name is not None
            result.macro = macro_name
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result


def parse_public_protected_private(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppPublicProtectedPrivate:
    """
    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types
    """
    access_type = element_c.tag()
    assert access_type in ["public", "protected", "private"]
    type = element_c.attribute_value("type")
    block_content = CppPublicProtectedPrivate(element_c, CppAccessType.from_name(access_type), type)
    block_content.parent = parent
    fill_block(options, element_c, block_content)
    return block_content


def parse_block(options: SrcmlcppOptions, element: SrcmlWrapper, parent: CppElementAndComment) -> CppBlock:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block
    """
    assert element.tag() == "block"

    cpp_block = CppBlock(element)
    cpp_block.parent = parent
    fill_block(options, element, cpp_block)
    return cpp_block


def is_operator_function(element_c: CppElementAndComment) -> bool:
    assert element_c.tag() in ["function", "function_decl"]
    type_attr = element_c.attribute_value("type")
    if type_attr is None:
        return False
    else:
        return type_attr == "operator"


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


def fill_extern_c_block(options: SrcmlcppOptions, element: SrcmlWrapper, inout_block_content: CppBlock) -> None:
    """
    Handle `extern "C"` blocks
    xml for
        extern "C" { void foo(); }'
    is
        <?xml version="1.0" ?>
        <unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++">
           <extern>
              extern
              <literal type="string">&quot;C&quot;</literal>
              <block>
                 {
                 <block_content>
                    <function_decl> <type> <name>void</name> </type> <name>foo</name> <parameter_list>()</parameter_list></function_decl>
                 </block_content>
                 }
              </block>
           </extern>
        </unit>

    """
    literal_elements = element.wrapped_children_with_tag("literal")
    if len(literal_elements) != 1:
        return
    extern_type = literal_elements[0].text()
    if extern_type != '"C"':
        return
    block_elements = element.wrapped_children_with_tag("block")
    if len(block_elements) != 1:
        return
    block_contents = block_elements[0].wrapped_children_with_tag("block_content")
    if len(block_contents) != 1:
        return
    fill_block(options, block_contents[0], inout_block_content)


def fill_block(options: SrcmlcppOptions, element: SrcmlWrapper, inout_block_content: CppBlock) -> None:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """

    last_ignored_child: Optional[CppElementAndComment] = None

    children: list[CppElementAndComment] = srcml_comments.get_children_with_comments(element)
    for _i, child_c in enumerate(children):
        global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_SRCML_PARSE, child_c.start().line)

        child_tag = child_c.tag()
        child_name = child_c.extract_name_from_xml()

        block_children = inout_block_content.block_children
        try:
            if child_tag == "decl_stmt":
                cpp_decl_stmt = parse_decl_stmt(options, child_c, inout_block_content)
                # Fix brace init default / functions
                fixed_function = fix_brace_init_default_value.change_decl_stmt_to_function_decl_if_suspicious(
                    options, cpp_decl_stmt
                )
                if fixed_function is not None:
                    fixed_function.parent = cpp_decl_stmt.parent
                    fixed_function._clear_scope_cache()
                    block_children.append(fixed_function)
                else:
                    block_children.append(cpp_decl_stmt)
            elif child_tag == "macro" and isinstance(inout_block_content, CppPublicProtectedPrivate):
                # Fixed brace init default / constructors
                macro_maybe_constructor = parse_unprocessed(options, child_c, inout_block_content)
                fixed_ctor = fix_brace_init_default_value.change_macro_to_constructor(options, macro_maybe_constructor)
                if fixed_ctor is not None:
                    block_children.append(fixed_ctor)
            elif child_tag == "decl":
                cpp_decl = parse_decl(options, child_c, inout_block_content, None)
                block_children.append(cpp_decl)
            elif child_tag in ["function_decl", "destructor_decl"]:
                assert child_name is not None
                block_children.append(parse_function_decl(options, child_c, inout_block_content))
            elif child_tag in ["function", "destructor"]:
                assert child_name is not None
                block_children.append(parse_function(options, child_c, inout_block_content))
            elif child_tag == "constructor_decl":
                block_children.append(parse_constructor_decl(options, child_c, inout_block_content))
            elif child_tag == "constructor":
                block_children.append(parse_constructor(options, child_c, inout_block_content))

            elif child_tag == "comment":
                cpp_comment = parse_comment(options, child_c, inout_block_content)

                if srcml_comments.EMPTY_LINE_COMMENT_CONTENT in cpp_comment.comment:
                    empty_line = CppEmptyLine(child_c)
                    empty_line.parent = inout_block_content
                    block_children.append(empty_line)
                else:
                    if not shall_ignore_comment(cpp_comment, last_ignored_child):
                        block_children.append(cpp_comment)

            elif child_tag == "struct" or child_tag == "class":
                # assert child_name is not None
                if child_name is None:
                    child_c.raise_exception("struct or class without name")
                block_children.append(parse_struct_or_class(options, child_c, inout_block_content))
            elif child_tag == "namespace":
                block_children.append(parse_namespace(options, child_c, inout_block_content))
            elif child_tag == "enum":
                block_children.append(parse_enum(options, child_c, inout_block_content))
            elif child_tag == "block_content":
                block_children.append(parse_block_content(options, child_c, inout_block_content))
            elif child_tag == "define":
                block_children.append(parse_define(options, child_c, inout_block_content))
            elif child_tag in [
                "if",
                "ifdef",
                "ifndef",
                "endif",
                "else",
                "elif",
            ]:  # #if, #ifdef, #ifndef, #endif, #else, #elif
                block_children.append(parse_condition_macro(options, child_c, inout_block_content))
            elif child_tag == "extern":
                fill_extern_c_block(options, child_c, inout_block_content)
            elif child_tag in ["public", "protected", "private"]:
                block_children.append(parse_public_protected_private(options, child_c, inout_block_content))
            else:
                last_ignored_child = child_c
                block_children.append(parse_unprocessed(options, child_c, inout_block_content))
        except SrcmlcppExceptionDetailed as e:
            block_children.append(parse_unprocessed(options, child_c, inout_block_content))
            element.emit_warning(
                f'A cpp element of type "{child_tag}" was stored as CppUnprocessed. Details follow\n{e}',
                WarningType.SrcmlcppIgnoreElement,
            )


def parse_unit(options: SrcmlcppOptions, element: SrcmlWrapper) -> CppUnit:
    assert element.tag() == "unit"
    cpp_unit = CppUnit(element)
    fill_block(options, element, cpp_unit)
    cpp_unit.fill_children_parents()
    return cpp_unit


def parse_block_content(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppBlockContent:  # element: SrcmlWrapper) -> CppBlockContent:
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """
    assert element_c.tag() == "block_content"

    block_content = CppBlockContent(element_c)
    block_content.parent = parent
    fill_block(options, element_c, block_content)
    return block_content


def parse_comment(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppComment:
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    """
    assert element_c.tag() == "comment"
    assert len(element_c.srcml_xml) == 0  # a comment has no child

    result = CppComment(element_c, element_c.cpp_element_comments)
    result.parent = parent

    comment = code_utils.str_none_empty(element_c.text())
    lines = comment.split("\n")
    if len(lines) > 1:
        lines = list(map(lambda line: "" if "_SRCML_EMPTY_LINE_" in line else line, lines))
        comment = "\n".join(lines)
        result.comment = comment
    else:
        result.comment = comment

    return result


def parse_namespace(
    options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment
) -> CppNamespace:
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    assert element_c.tag() == "namespace"
    result = CppNamespace(element_c, element_c.cpp_element_comments)
    result.parent = parent
    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.ns_name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child, element_c)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")
    return result


def parse_enum(options: SrcmlcppOptions, element_c: CppElementAndComment, parent: CppElementAndComment) -> CppEnum:
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """
    assert element_c.tag() == "enum"
    result = CppEnum(element_c, element_c.cpp_element_comments)
    result.parent = parent

    if "type" in element_c.srcml_xml.attrib.keys():
        enum_type = element_c.attribute_value("type")
        assert enum_type is not None
        result.enum_type = enum_type

    for child in element_c.make_wrapped_children():
        child_tag = child.tag()
        if child_tag == "name":
            result.enum_name = _parse_name(child)
        elif child_tag == "block":
            result.block = parse_block(options, child, element_c)
        elif child_tag == "comment":
            _add_comment_child_before_block(result, child)
        elif child_tag == "type":
            name_children = child.wrapped_children_with_tag("name")
            if len(name_children) == 1:
                enum_data_type = name_children[0].text()
                if enum_data_type is not None:
                    result.enum_data_type = enum_data_type
        else:
            raise SrcmlcppExceptionDetailed(child, f"unhandled tag {child_tag}")

    return result
