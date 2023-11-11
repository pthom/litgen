from __future__ import annotations
import srcmlcpp
from srcmlcpp import SrcmlWrapper
from codemanip import code_utils


def cpp_to_snake_case(cpp_code: str) -> str:
    options = srcmlcpp.SrcmlcppOptions()
    root_wrapper = srcmlcpp.code_to_srcml_wrapper(options, cpp_code)

    def visitor_to_snake_case(element: SrcmlWrapper, _depth: int) -> None:
        if element.tag() in ["function", "function_decl", "decl"]:
            if element.has_xml_name():
                old_name = element.extract_name_from_xml()
                assert old_name is not None
                new_name = code_utils.to_snake_case(old_name)
                element.change_name_child_text(new_name)
        if element.tag() == "comment":
            element_text = element.text()
            if element_text is not None:
                if "// _SRCML_EMPTY_LINE_" in element_text:
                    element.set_text("")

    root_wrapper.visit_xml_breadth_first(visitor_to_snake_case)
    r = root_wrapper.str_code_verbatim()
    return r


def cpp_to_python_helper(cpp_code: str) -> str:
    cpp_snake_case = cpp_to_snake_case(cpp_code)

    python_code = cpp_snake_case
    python_code = python_code.replace("::", ".")
    python_code = python_code.replace("{", "")
    python_code = python_code.replace("}", "")
    return python_code
