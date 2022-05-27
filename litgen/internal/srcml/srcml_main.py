from typing import List
import xml.etree.ElementTree as ET

from litgen.internal.srcml import srcml_types, srcml_comments, srcml_types_parse
from litgen.internal import srcml
from litgen import CodeStyleOptions

_CURRENT_PARSED_FILE: str = ""
_CURRENT_PARSED_UNIT_CODE: str = ""


def current_parsed_file():
    return _CURRENT_PARSED_FILE


def current_parsed_unit_code():
    return _CURRENT_PARSED_UNIT_CODE


def get_children_with_comments(options: CodeStyleOptions, srcml_xml: ET.Element) -> List[srcml_types.CppElementAndComment]:
    if options.header_filter_preprocessor_regions:
        srcml_xml = srcml.srcml_filter_preprocessor_regions.filter_preprocessor_regions(
            srcml_xml, options.header_guard_suffixes)

    cpp_elements_commented = srcml_comments.get_children_with_comments(srcml_xml)
    return cpp_elements_commented


def code_to_srcml_unit(options: CodeStyleOptions, code: str = "", filename: str = "") -> ET.Element:
    """Parse the given code, and returns it under the form of a srcML unit element
    Note:
        * if `code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """
    global _CURRENT_PARSED_FILE, _CURRENT_PARSED_UNIT_CODE
    _CURRENT_PARSED_FILE = filename

    if len(code) == 0:
        with open(filename, "r", encoding=options.encoding) as f:
            code = f.read()

    _CURRENT_PARSED_UNIT_CODE = code

    if options.code_preprocess_function is not None:
        code = options.code_preprocess_function(code)

    if options.preserve_empty_lines:
        code = srcml_comments._mark_empty_lines(code)

    srcml_xml = srcml.srcml_caller.code_to_srcml(code, encoding=options.encoding)

    return srcml_xml


def file_to_srcml_unit(options: CodeStyleOptions, filename: str) -> ET.Element:
    """Parse the given file, and returns it under the form of a srcML unit element"""
    return code_to_srcml_unit(options, filename=filename)


def code_to_cpp_unit(options: CodeStyleOptions, code: str = "", filename: str = "") -> srcml_types.CppUnit:
    srcml_unit = code_to_srcml_unit(options, code, filename)
    cpp_unit = srcml_types_parse.parse_unit(options, srcml_unit)
    return cpp_unit


def file_to_cpp_unit(options: CodeStyleOptions, filename: str = "") -> srcml_types.CppUnit:
    srcml_unit = code_to_srcml_unit(options, filename=filename)
    cpp_unit = srcml_types_parse.parse_unit(options, srcml_unit)
    return cpp_unit


def get_only_child_with_tag(options: CodeStyleOptions, code: str, tag: str) -> srcml_types.CppElementAndComment:
    srcml_unit = code_to_srcml_unit(options, code)
    children = get_children_with_comments(options, srcml_unit)
    children_with_tag = list(filter(lambda child: child.tag() == tag, children))
    assert len(children_with_tag) == 1
    return children_with_tag[0]


def get_unit_children(options: CodeStyleOptions, code: str) -> List[srcml_types.CppElementAndComment]:
    srcml_unit = srcml.srcml_main.code_to_srcml_unit(options, code)
    children = srcml.srcml_main.get_children_with_comments(options, srcml_unit)
    return children
