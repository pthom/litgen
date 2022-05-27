import logging
from typing import List
from dataclasses import dataclass
from srcml import srcml_types, srcml_comments, srcml_utils
from litgen import CodeStyleOptions


@dataclass
class CppDecl:
    name: str = ""
    type: str = ""
    default_value: str = ""


@dataclass
class CppFunctionDecl:
    name: str
    parameters: List[CppDecl]
    return_type: str
    srcml_element: srcml_types.CppElementAndComment

    # See https://pybind11-jagerman.readthedocs.io/en/stable/advanced.html?highlight=reference#return-value-policies
    # If you annotate a function declaration, you can set the return value lifetime policy:
    # For example:
    #       ````cpp
    #       Foo& getFoo()    // return_value_policy::reference
    #       ````
    return_value_policy: str = ""

    def __init__(self):
        self.parameters: List[CppDecl] = []


def srcml_decl_to_cpp_decl(srcml_element_with_comment: srcml_types.CppElementAndComment,
                           options: CodeStyleOptions) -> CppDecl:
    assert srcml_element_with_comment.tag() == "decl"
    result = CppDecl()

    children = srcml_comments.get_children_with_comments(srcml_element_with_comment.srcml_element)

    return result


def srcml_function_to_cpp_function_decl(
        srcml_element_with_comment: srcml_types.CppElementAndComment,
        options: CodeStyleOptions) -> CppFunctionDecl:
    assert srcml_element_with_comment.tag() == "function" or srcml_element_with_comment.tag() == "function_decl"

    result = CppFunctionDecl()

    # return_value_policy
    token = "return_value_policy::"
    if token in srcml_element_with_comment.comment_end_of_line:
        result.return_value_policy = srcml_element_with_comment.comment_end_of_line[
                                     srcml_element_with_comment.comment_end_of_line.index(token) + len(token) : ]
        srcml_element_with_comment.comment_end_of_line = ""

    logging.warning(srcml_utils.srcml_to_str_readable(srcml_element_with_comment.srcml_element))
    #for child in srcml_comments.get_children_with_comments()

