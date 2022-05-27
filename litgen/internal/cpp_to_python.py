"""
Apply some replacements when going from c++ to Python:
- CamelCase to snake_case
- double -> float, void -> None, etc.

"""
from typing import List
# from code_types import *
from litgen import CodeStyleOptions, LitgenParseException
import code_replacements, code_utils


def docstring_python(title_cpp: str, options: CodeStyleOptions) -> str:
    """
    Make some replacements in a C++ title (a comment on top of a function, struct, etc)
    in order to adapt it to python.
    """
    return code_replacements.apply_code_replacements(title_cpp, options.code_replacements)


def docstring_python_one_line(title_cpp: str, options: CodeStyleOptions) -> str:
    return code_utils.format_cpp_comment_on_one_line(docstring_python(title_cpp, options))


def type_to_python(type_cpp: str, options: CodeStyleOptions) -> str:
    return code_replacements.apply_code_replacements(type_cpp, options.code_replacements)


# def attr_cpp_type_name_default(attr: PydefAttribute) -> str:
#     default_value_cpp_str = ""
#     if len(attr.default_value_cpp) > 0:
#         default_value_cpp_str = " = " + attr.default_value_cpp
#     cpp_str = f"{attr.type_cpp} {attr.name_cpp}{default_value_cpp_str}"
#     return cpp_str
#
#
# def attrs_cpp_type_name_default(attrs: List[PydefAttribute]) -> str:
#     strs = map(attr_cpp_type_name_default, attrs)
#     return ", ".join(strs)
#
#
# def attr_python_name_type_default(attr: PydefAttribute, options: CodeStyleOptions) -> str:
#     var_name_python = var_name_to_python(attr.name_cpp, options)
#     var_type_python = type_to_python(attr.type_cpp, options)
#     default_value_python = default_value_to_python(attr.default_value_cpp, options)
#
#     python_str = var_name_python
#     if len(var_type_python) > 0:
#         python_str += ": " + var_type_python
#     if len(default_value_python) > 0:
#         python_str += " = " + default_value_python
#     return python_str
#
#
# def attrs_python_name_type_default(attrs: List[PydefAttribute], options: CodeStyleOptions) -> str:
#     strs = list(map(lambda attr: attr_python_name_type_default(attr, options), attrs))
#     return ", ".join(strs)


def var_name_to_python(var_name: str, options: CodeStyleOptions) -> str:
    return code_utils.to_snake_case(var_name)


def function_name_to_python(function_name: str, options: CodeStyleOptions) -> str:
    return code_utils.to_snake_case(function_name)


# def params_names_to_python(params: List[PydefAttribute], options: CodeStyleOptions) -> str:
#     params_list = []
#     for param in params:
#         params_list.append(var_name_to_python(param.name_cpp, options))
#     r = ", ".join(params_list)
#     return r


def default_value_to_python(default_value_cpp: str, options: CodeStyleOptions) -> str:
    return code_replacements.apply_code_replacements(default_value_cpp, options.code_replacements)


"""
In python and numpy we have the following correspondence:

Given a py::array, we can get its inner type with a char identifier like this: 
    char array_type = array.dtype().char_();

Here is the table of correspondences:
"""
_PY_ARRAY_TYPE_TO_CPP_TYPE = {
    'B' : 'uint8_t',
    'b' : 'int8_t',
    'H' : 'uint16_t',
    'h' : 'int16_t',
    'I' : 'uint32_t',
    'i' : 'int32_t',
    'L' : 'uint64_t',
    'l' : 'int64_t',
    'f' : 'float',
    'd' : 'double',
    'g' : 'long double'
}


def py_array_types():
    return _PY_ARRAY_TYPE_TO_CPP_TYPE.keys()


def py_array_type_to_cpp_type(py_array_type: str) -> str:
    assert len(py_array_type) == 1
    assert py_array_type in _PY_ARRAY_TYPE_TO_CPP_TYPE
    return _PY_ARRAY_TYPE_TO_CPP_TYPE[py_array_type]


def cpp_type_to_py_array_type(cpp_type: str) -> str:
    cpp_type = cpp_type.strip()
    if cpp_type.endswith("*"):
        cpp_type = cpp_type[:-1].strip()
    if cpp_type.startswith("const "):
        cpp_type = cpp_type.replace("const ", "").strip()
    for py_type, tested_cpp_type in _PY_ARRAY_TYPE_TO_CPP_TYPE.items():
        if tested_cpp_type == cpp_type:
            return py_type
    raise LitgenParseException(f"cpp_type_to_py_array_type: unhandled type {cpp_type}")


def _enum_remove_values_prefix(enum_name: str, value_name: str) -> str:
    if value_name.upper().startswith(enum_name.upper() + "_"):
        return value_name[len(enum_name) + 1 : ]
    elif value_name.upper().startswith(enum_name.upper()):
        return value_name[len(enum_name) : ]
    else:
        return value_name


def enum_value_name_to_python(enum_name: str, value_name: str, options: CodeStyleOptions) -> str:
    if options.enum_flag_remove_values_prefix:
        value_name = _enum_remove_values_prefix(enum_name, value_name)
    return var_name_to_python(value_name, options)


def enum_value_name_is_count(enum_name: str, value_name: str, options: CodeStyleOptions) -> bool:
    if not options.enum_flag_skip_count:
        return False
    return (value_name.lower() == enum_name.lower() + "_count"
            or value_name.lower() == enum_name.lower() + "count"
            or value_name.lower() == "count")
