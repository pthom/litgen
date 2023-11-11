from __future__ import annotations
from codemanip import code_utils

from litgen.internal import cpp_to_python
from litgen.internal.context.litgen_context import LitgenContext


def _can_box_cpp_type(cpp_type: str) -> bool:
    r = cpp_to_python.is_cpp_type_immutable_for_python(cpp_type)
    return r


def boxed_type_name(cpp_type: str) -> str:
    assert _can_box_cpp_type(cpp_type)
    if cpp_type == "std::string":
        cpp_type = "string"
    boxed_name = "Boxed" + cpp_to_python.cpp_type_to_camel_case_no_space(cpp_type)
    return boxed_name


def registered_boxed_type_name(context: LitgenContext, cpp_type: str) -> str:
    context.encountered_cpp_boxed_types.add(cpp_type)
    return boxed_type_name(cpp_type)


def boxed_type_cpp_struct_code(cpp_type: str, indent_str: str) -> str:
    assert _can_box_cpp_type(cpp_type)
    cpp_type_default_value = cpp_to_python.cpp_type_default_python_value(cpp_type)
    assert cpp_type_default_value is not None

    struct_name = boxed_type_name(cpp_type)
    _i_ = indent_str

    std_to_string_value = "std::to_string(value)"
    if cpp_type in ["string", "std::string"]:
        std_to_string_value = "value"

    struct_code = f"""
        struct {struct_name}
        {{
        {_i_}{cpp_type} value;
        {_i_}{struct_name}({cpp_type} v = {cpp_type_default_value}) : value(v) {{}}
        {_i_}std::string __repr__() const {{ return std::string("{struct_name}(") + {std_to_string_value} + ")"; }}
        }};
    """
    struct_code = code_utils.unindent_code(struct_code, flag_strip_empty_lines=True) + "\n"
    return struct_code
