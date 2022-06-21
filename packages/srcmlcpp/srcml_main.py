import logging
from dataclasses import dataclass
from typing import List, Optional, Type, cast, TypeVar
from xml.etree import ElementTree as ET

from srcmlcpp import (
    srcml_caller,
    srcml_comments,
    srcml_filter_preprocessor_regions,
    srcml_types,
    srcml_types_parse,
    srcml_utils,
    srcml_warnings,
)
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_types import *


@dataclass
class _SrcmlMainContext:
    _current_parsed_file: str = ""
    _current_parsed_file_unit_code: str = ""

    # def __init__(self):
    #     logging.warning(f"Constructing _SrcmlMainContext id={id(self)}")

    @property
    def current_parsed_file(self):
        return self._current_parsed_file

    @current_parsed_file.setter
    def current_parsed_file(self, value):
        self._current_parsed_file = value

    @property
    def current_parsed_file_unit_code(self):
        return self._current_parsed_file_unit_code

    @current_parsed_file_unit_code.setter
    def current_parsed_file_unit_code(self, value):
        self._current_parsed_file_unit_code = value


def srcml_main_context() -> _SrcmlMainContext:
    if not hasattr(srcml_main_context, "instance"):
        srcml_main_context.instance = _SrcmlMainContext()  # type: ignore
    return srcml_main_context.instance  # type: ignore


def get_children_with_comments(options: SrcmlOptions, srcml_xml: ET.Element) -> List[srcml_types.CppElementAndComment]:
    if options.header_filter_preprocessor_regions:
        srcml_xml = srcml_filter_preprocessor_regions.filter_preprocessor_regions(
            srcml_xml, options.header_guard_suffixes
        )

    cpp_elements_commented = srcml_comments.get_children_with_comments(srcml_xml)
    return cpp_elements_commented


def code_to_srcml_unit(options: SrcmlOptions, code: str = "", filename: str = "") -> ET.Element:
    """Parse the given code, and returns it under the form of a srcML unit element
    Note:
        * if `code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """

    if len(filename) > 0:
        srcml_main_context().current_parsed_file = filename

    if len(code) == 0:
        with open(filename, "r", encoding=options.encoding) as f:
            code = f.read()

    if len(filename) > 0:
        srcml_main_context().current_parsed_file_unit_code = code

    if options.code_preprocess_function is not None:
        code = options.code_preprocess_function(code)

    if options.preserve_empty_lines:
        code = srcml_comments.mark_empty_lines(code)

    srcml_xml = srcml_caller.code_to_srcml(code, encoding=options.encoding)

    return srcml_xml


def file_to_srcml_unit(options: SrcmlOptions, filename: str) -> ET.Element:
    """Parse the given file, and returns it under the form of a srcML unit element"""
    return code_to_srcml_unit(options, filename=filename)


def code_to_cpp_unit(options: SrcmlOptions, code: str = "", filename: str = "") -> srcml_types.CppUnit:
    srcml_unit = code_to_srcml_unit(options, code, filename)
    cpp_unit = srcml_types_parse.parse_unit(options, srcml_unit)
    return cpp_unit


def file_to_cpp_unit(options: SrcmlOptions, filename: str = "") -> srcml_types.CppUnit:
    srcml_unit = code_to_srcml_unit(options, filename=filename)
    cpp_unit = srcml_types_parse.parse_unit(options, srcml_unit)
    return cpp_unit


def code_first_child_of_type(
    options: SrcmlOptions, type_of_cpp_element: Type, code: str
) -> srcml_types.CppElementAndComment:
    cpp_unit = code_to_cpp_unit(options, code)
    for child in cpp_unit.block_children:
        if isinstance(child, type_of_cpp_element):
            return child  # type: ignore
    raise srcml_warnings.SrcMlException(f"Could not find a child of type {type_of_cpp_element}")


def code_first_function_decl(options: SrcmlOptions, code: str) -> srcml_types.CppFunctionDecl:
    return cast(CppFunctionDecl, code_first_child_of_type(options, CppFunctionDecl, code))


def code_first_enum(options: SrcmlOptions, code: str) -> srcml_types.CppEnum:
    return cast(CppEnum, code_first_child_of_type(options, CppEnum, code))


def code_first_decl(options: SrcmlOptions, code: str) -> srcml_types.CppDecl:
    return cast(CppDecl, code_first_child_of_type(options, CppDecl, code))


def code_first_struct(options: SrcmlOptions, code: str) -> srcml_types.CppStruct:
    return cast(CppStruct, code_first_child_of_type(options, CppStruct, code))


def code_first_class(options: SrcmlOptions, code: str) -> srcml_types.CppClass:
    return cast(CppClass, code_first_child_of_type(options, CppClass, code))


def _tests_only_get_only_child_with_tag(options: SrcmlOptions, code: str, tag: str) -> srcml_types.CppElementAndComment:
    srcml_unit = code_to_srcml_unit(options, code)
    children = get_children_with_comments(options, srcml_unit)
    children_with_tag = list(filter(lambda child: child.tag() == tag, children))
    assert len(children_with_tag) == 1
    return children_with_tag[0]
