"""
Main functions provided by this module

* `code_to_cpp_unit` is the main entry. It will transform code into a tree of Cpp elements

* `code_to_srcml_xml_wrapper` is a lower level utility, that returns a wrapped version of the srcML tree
"""

from typing import Optional, Type, cast

from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp import SrcmlWrapper
from srcmlcpp.cpp_types import *
from srcmlcpp.internal import (
    code_cache,
    srcml_caller,
    srcml_comments,
    srcml_types_parse,
)
from srcmlcpp.srcml_exception import SrcmlException
from srcmlcpp.srcml_options import SrcmlOptions


def _code_or_file_content(options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None) -> str:
    if code is None:
        if filename is None:
            raise ValueError("Either cpp_code or filename needs to be specified!")
        assert filename is not None  # make mypy happy
        with open(filename, "r", encoding=options.encoding) as f:
            code_str = f.read()
    else:
        code_str = code
    return code_str


def code_to_srcml_xml_wrapper(
    options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> SrcmlWrapper:
    """Create a srcML tree from c++ code, and wraps it into a SrcmlWrapper

    Note:
        * if `cpp_code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """
    code = _code_or_file_content(options, code, filename)

    if options.code_preprocess_function is not None:
        code = options.code_preprocess_function(code)

    code_cache.store_cached_code(filename, code)

    if options.preserve_empty_lines:
        code = srcml_comments.mark_empty_lines(code)

    xml = srcml_caller.code_to_srcml(code, dump_positions=options.flag_srcml_dump_positions, encoding=options.encoding)

    r = SrcmlWrapper(options, xml, filename)
    return r


def nb_lines_in_code_or_file(options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None) -> int:
    code_str = _code_or_file_content(options, code, filename)
    nb_lines = code_str.count("\n")
    return nb_lines


def _code_to_cpp_unit_impl(
    options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> CppUnit:
    xml_wrapper = code_to_srcml_xml_wrapper(options, code, filename)
    cpp_unit = srcml_types_parse.parse_unit(options, xml_wrapper)
    return cpp_unit


def code_to_cpp_unit(options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None) -> CppUnit:
    if options.flag_show_progress:
        nb_lines = nb_lines_in_code_or_file(options, code, filename)
        global_progress_bars().set_nb_total_lines(nb_lines)
        global_progress_bars().set_enabled(True)
    else:
        global_progress_bars().set_enabled(False)

    from srcmlcpp.internal.srcml_types_parse import _PROGRESS_BAR_TITLE_SRCML_PARSE

    global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_SRCML_PARSE)
    cpp_unit = _code_to_cpp_unit_impl(options, code, filename)
    global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_SRCML_PARSE)
    return cpp_unit


def code_first_child_of_type(
    options: SrcmlOptions, type_of_cpp_element: Type[CppElement], code: str
) -> CppElementAndComment:
    cpp_unit = _code_to_cpp_unit_impl(options, code)
    for child in cpp_unit.block_children:
        if isinstance(child, type_of_cpp_element):
            return child
    raise SrcmlException(f"Could not find a child of type {type_of_cpp_element}")


def code_first_function_decl(options: SrcmlOptions, code: str) -> CppFunctionDecl:
    return cast(CppFunctionDecl, code_first_child_of_type(options, CppFunctionDecl, code))


def code_first_enum(options: SrcmlOptions, code: str) -> CppEnum:
    return cast(CppEnum, code_first_child_of_type(options, CppEnum, code))


def code_first_decl_statement(options: SrcmlOptions, code: str) -> CppDeclStatement:
    return cast(CppDeclStatement, code_first_child_of_type(options, CppDeclStatement, code))


def code_first_decl(options: SrcmlOptions, code: str) -> CppDecl:
    return cast(CppDecl, code_first_child_of_type(options, CppDecl, code))


def code_first_struct(options: SrcmlOptions, code: str) -> CppStruct:
    return cast(CppStruct, code_first_child_of_type(options, CppStruct, code))


def code_to_cpp_type(options: SrcmlOptions, code: str) -> CppType:
    code_plus_dummy_var = code + " dummy;"
    first_decl_statement = code_first_decl_statement(options, code_plus_dummy_var)
    first_decl = first_decl_statement.cpp_decls[0]
    cpp_type = first_decl.cpp_type
    return cpp_type


def _tests_only_get_only_child_with_tag(options: SrcmlOptions, code: str, tag: str) -> CppElementAndComment:
    from srcmlcpp.internal import srcml_comments

    srcml_unit = code_to_srcml_xml_wrapper(options, code)
    children = srcml_comments.get_children_with_comments(srcml_unit)
    children_with_tag = list(filter(lambda child: child.tag() == tag, children))
    assert len(children_with_tag) == 1
    return children_with_tag[0]
