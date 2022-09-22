"""
Main functions provided by this module

* `code_to_cpp_unit` is the main entry. It will transform code into a tree of Cpp elements

* `code_to_srcml_xml_wrapper` is a lower level utility, that returns a wrapped version of the srcML tree
"""

from typing import Type

from srcmlcpp.internal import srcml_comments
from srcmlcpp.srcml_types import *
from srcmlcpp.internal import srcml_caller
from srcmlcpp.internal import srcml_types_parse
from srcmlcpp.srcml_exception import SrcMlException


_Filename = str
_Code = str
_CODE_CACHE: Dict[Optional[_Filename], _Code] = {}


def _get_cached_file_code(filename: Optional[str]) -> str:
    if filename not in _CODE_CACHE.keys():
        raise ValueError(f"filename {filename} not in code cache!")
    return _CODE_CACHE[filename]


def code_to_srcml_xml_wrapper(
    options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> SrcmlXmlWrapper:
    """Create a srcML tree from c++ code, and wraps it into a SrcmlXmlWrapper

    Note:
        * if `cpp_code` is not empty, the code will be taken from it.
          In this case, the `filename` param will still be used to display code source position in warning messages.
          This can be used when you need to preprocess the code before parsing it.
        * if `code`is empty, the code will be read from `filename`
    """
    if code is None:
        if filename is None:
            raise ValueError("Either cpp_code or filename needs to be specified!")
        assert filename is not None  # make mypy happy
        with open(filename, "r", encoding=options.encoding) as f:
            code = f.read()

    if options.code_preprocess_function is not None:
        code = options.code_preprocess_function(code)

    global _CODE_CACHE
    _CODE_CACHE[filename] = code

    if options.preserve_empty_lines:
        code = srcml_comments.mark_empty_lines(code)

    xml = srcml_caller.code_to_srcml(code, dump_positions=options.srcml_dump_positions, encoding=options.encoding)

    r = SrcmlXmlWrapper(options, xml, filename)
    return r


def code_to_cpp_unit(options: SrcmlOptions, code: Optional[str] = None, filename: Optional[str] = None) -> CppUnit:
    xml_wrapper = code_to_srcml_xml_wrapper(options, code, filename)
    cpp_unit = srcml_types_parse.parse_unit(options, xml_wrapper)
    return cpp_unit


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
