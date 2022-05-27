import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

from litgen.internal import srcml, CodeStyleOptions, cpp_to_python, code_utils, cpp_elements
from litgen.internal.srcml.srcml_types import CppElementAndComment


def _generate_pydef_enum(enum_with_comments: CppElementAndComment, options: CodeStyleOptions) -> str:
    enum_type = enum_with_comments.attribute_value("type")
    enum_name = enum_with_comments.name()

    code_intro = f'    py::enum_<{enum_name}>(m, "{enum_name}", py::arithmetic(),\n'
    comment = cpp_to_python.docstring_python_one_line(enum_with_comments.cpp_element_comments.full_comment(), options)
    code_intro += f'        "{comment}")\n'
    code_inner = f'        .value("VALUE_NAME_PYTHON", VALUE_NAME_CPP, "(VALUE_COMMENT)")\n'
    code_outro = "    ;\n\n"
    final_code = code_intro

    def make_value_code(enum_decl: CppElementAndComment):
        code = code_inner
        value_name_cpp = enum_decl.name()
        value_name_python = cpp_to_python.enum_value_name_to_python(enum_name, value_name_cpp, options)

        if enum_type == "class":
            value_name_cpp_str = enum_name + "::" + value_name_cpp
        else:
            value_name_cpp_str = value_name_cpp

        code = code.replace("VALUE_NAME_PYTHON", value_name_python)
        code = code.replace("VALUE_NAME_CPP", value_name_cpp_str)
        code = code.replace("VALUE_COMMENT", code_utils.format_cpp_comment_on_one_line(
            enum_decl.cpp_element_comments.full_comment()))

        if cpp_to_python.enum_value_name_is_count(enum_name, value_name_cpp, options):
            return ""
        return code

    block_element = srcml.srcml_utils.child_with_tag(enum_with_comments.srcml_element, "block")
    for child in srcml.srcml_comments.get_children_with_comments(block_element):
        if child.tag() == "comment":
            final_code += f"        // {child.text()}\n"
        elif child.tag() == "decl":
            final_code = final_code + make_value_code(child)
        else:
            raise srcml.SrcMlException(child.srcml_element, f"Unexpected tag {child.tag()} in enum")
    final_code = final_code + code_outro
    return final_code


def _generate_pydef_function(srcml_function: CppElementAndComment, options: CodeStyleOptions) -> str:
    cpp_function_decl = cpp_elements.srcml_function_to_cpp_function_decl(srcml_function)
    return ""


def generate_pydef(code: str, options: CodeStyleOptions) -> str:
    elements = srcml.srcml_main.get_unit_children(options, code)
    r = ""
    for element in elements:
        if element.tag() == "enum":
            r += _generate_pydef_enum(element, options)
        elif element.tag() == "function" or element.tag() == "function_decl":
            r += _generate_pydef_function(element, options)
    return r
