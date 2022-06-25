from typing import Optional, List, Type, cast

from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_xml_wrapper import SrcmlXmlWrapper
from srcmlcpp.internal import srcml_comments
from srcmlcpp.srcml_types import *
from srcmlcpp.filter_preprocessor_regions import filter_preprocessor_regions
from srcmlcpp.internal import srcml_caller
from srcmlcpp.srcml_exception import SrcMlException

#
# @dataclass
# class _SrcmlMainContext:
#     _current_parsed_file: str = ""
#     _current_parsed_file_unit_code: str = ""
#
#     # def __init__(self):
#     #     logging.warning(f"Constructing _SrcmlMainContext id={id(self)}")
#
#     @property
#     def current_parsed_file(self):
#         return self._current_parsed_file
#
#     @current_parsed_file.setter
#     def current_parsed_file(self, value):
#         self._current_parsed_file = value
#
#     @property
#     def current_parsed_file_unit_code(self):
#         return self._current_parsed_file_unit_code
#
#     @current_parsed_file_unit_code.setter
#     def current_parsed_file_unit_code(self, value):
#         self._current_parsed_file_unit_code = value
#


def _get_cached_file_code(filename: Optional[str]) -> str:
    pass


def code_to_srcml_xml_wrapper(
    options: SrcmlOptions, cpp_code: Optional[str] = None, filename: Optional[str] = None
) -> SrcmlXmlWrapper:
    """Create a srcML tree from c++ code, and wraps it into a SrcmlXmlWrapper

    Note:
        * if `cpp_code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """
    if cpp_code is None:
        if filename is None:
            raise ValueError("Either cpp_code or filename needs to be specified!")
        assert filename is not None  # make mypy happy
        with open(filename, "r", encoding=options.encoding) as f:
            cpp_code = f.read()

    if options.code_preprocess_function is not None:
        cpp_code = options.code_preprocess_function(cpp_code)

    if options.preserve_empty_lines:
        cpp_code = srcml_comments.mark_empty_lines(cpp_code)

    xml = srcml_caller.code_to_srcml(cpp_code, dump_positions=options.srcml_dump_positions, encoding=options.encoding)

    if options.header_filter_preprocessor_regions:
        xml = filter_preprocessor_regions(xml, options.header_guard_suffixes)

    r = SrcmlXmlWrapper(options, xml, filename)
    return r


def code_to_cpp_unit(options: SrcmlOptions, cpp_code: Optional[str] = None, filename: Optional[str] = None) -> CppUnit:
    pass


def code_first_child_of_type(options: SrcmlOptions, type_of_cpp_element: Type, code: str) -> CppElementAndComment:
    cpp_unit = code_to_cpp_unit(options, code)
    for child in cpp_unit.block_children:
        if isinstance(child, type_of_cpp_element):
            return child  # type: ignore
    raise SrcMlException(f"Could not find a child of type {type_of_cpp_element}")


def code_first_function_decl(options: SrcmlOptions, code: str) -> CppFunctionDecl:
    return cast(CppFunctionDecl, code_first_child_of_type(options, CppFunctionDecl, code))


def code_first_enum(options: SrcmlOptions, code: str) -> CppEnum:
    return cast(CppEnum, code_first_child_of_type(options, CppEnum, code))


def code_first_decl(options: SrcmlOptions, code: str) -> CppDecl:
    return cast(CppDecl, code_first_child_of_type(options, CppDecl, code))


def code_first_struct(options: SrcmlOptions, code: str) -> CppStruct:
    return cast(CppStruct, code_first_child_of_type(options, CppStruct, code))


def _tests_only_get_only_child_with_tag(options: SrcmlOptions, code: str, tag: str) -> CppElementAndComment:
    from srcmlcpp.internal import srcml_comments

    srcml_unit = code_to_srcml_xml_wrapper(options, code)
    children = srcml_comments.get_children_with_comments(srcml_unit)
    children_with_tag = list(filter(lambda child: child.tag() == tag, children))
    assert len(children_with_tag) == 1
    return children_with_tag[0]
