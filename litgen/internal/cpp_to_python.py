from typing import List
from dataclasses import dataclass
from litgen import CodeStyleOptions
from litgen.internal import code_replacements, code_utils

"""
Apply some replacements when going from c++ to Python:
- CamelCase to snake_case
- double -> float, void -> None, etc.

"""


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


def var_name_to_python(var_name: str, options: CodeStyleOptions) -> str:
    return code_utils.to_snake_case(var_name)


def function_name_to_python(function_name: str, options: CodeStyleOptions) -> str:
    return code_utils.to_snake_case(function_name)


def default_value_to_python(default_value_cpp: str, options: CodeStyleOptions) -> str:
    return code_replacements.apply_code_replacements(default_value_cpp, options.code_replacements)


def _cpp_type_to_camel_case_no_space(cpp_type: str) -> str:
    items = cpp_type.split(" ")

    def capitalize_first_letter(s: str):
        return s[0].upper() + s[1:]
    items = list(map(capitalize_first_letter, items))

    r = "".join(items)
    return r


@dataclass
class CppPythonTypesSynonyms:
    cpp_type: str
    python_type: str


CPP_PYTHON_NUMERIC_SYNONYMS = [
    CppPythonTypesSynonyms("int", "int"),
    CppPythonTypesSynonyms("unsigned int", "int"),
    CppPythonTypesSynonyms("long", "int"),
    CppPythonTypesSynonyms("unsigned long", "int"),
    CppPythonTypesSynonyms("long long", "int"),
    CppPythonTypesSynonyms("unsigned long long", "int"),

    CppPythonTypesSynonyms("float", "float"),
    CppPythonTypesSynonyms("double", "float"),
    CppPythonTypesSynonyms("long double", "float"),

    CppPythonTypesSynonyms('uint8_t', 'int'),
    CppPythonTypesSynonyms('int8_t', 'int'),
    CppPythonTypesSynonyms('uint16_t', 'int'),
    CppPythonTypesSynonyms('int16_t', 'int'),
    CppPythonTypesSynonyms('uint32_t', 'int'),
    CppPythonTypesSynonyms('int32_t', 'int'),
    CppPythonTypesSynonyms('uint64_t', 'int'),
    CppPythonTypesSynonyms('int64_t', 'int'),
]


def cpp_numeric_types():
    r = []
    for t in CPP_PYTHON_NUMERIC_SYNONYMS:
        r.append(t.cpp_type)
    return r


def is_cpp_type_immutable_in_python(cpp_type: str):
    if cpp_type in cpp_numeric_types():
        return True
    if cpp_type in ["string", "std::string"]:
        return True
    # Etc: handle tuple and complex numbers?
    return False


class BoxedImmutablePythonType:
    static_list_of_instantiated_type = []
    cpp_type: str

    def __init__(self, cpp_type: str):
        if not is_cpp_type_immutable_in_python(cpp_type):
            raise TypeError(f"BoxedImmutablePythonType({cpp_type}) is seemingly not immutable")
        self.cpp_type = cpp_type
        if cpp_type not in BoxedImmutablePythonType.static_list_of_instantiated_type:
            BoxedImmutablePythonType.static_list_of_instantiated_type.append(cpp_type)

    def boxed_type_name(self):
        boxed_name = "Boxed" + _cpp_type_to_camel_case_no_space(self.cpp_type)
        return boxed_name

    def _struct_code(self) -> str:
        struct_name = self.boxed_type_name()

        struct_code = f"""
            struct {struct_name}
            {{
                {self.cpp_type} value;
                {struct_name}() : value{{}} {{}}
                {struct_name}({self.cpp_type} v) : value(v) {{}}
                std::string __repr__() {{ return std::string("{struct_name}(") + std::to_string(value) + ")"; }}
            }};
        """
        struct_code = code_utils.unindent_code(struct_code, flag_strip_empty_lines=True)
        return struct_code

    def _binding_code(self, options: CodeStyleOptions) -> str:
        from litgen import generate_code
        struct_code = self._struct_code()
        pydef_code = generate_code.generate_pydef(struct_code, options, add_boxed_types_definitions=False)
        return pydef_code

    @staticmethod
    def struct_codes():
        r = ""
        for cpp_type in BoxedImmutablePythonType.static_list_of_instantiated_type:
            boxed_type = BoxedImmutablePythonType(cpp_type)
            r += boxed_type._struct_code() + "\n"
        return r

    @staticmethod
    def binding_codes(options: CodeStyleOptions):
        r = ""
        for cpp_type in BoxedImmutablePythonType.static_list_of_instantiated_type:
            boxed_type = BoxedImmutablePythonType(cpp_type)
            r += boxed_type._binding_code(options)
        return r


# def get_cpp_numeric_synonyms(cpp_type: str) -> CppPythonTypesSynonyms:
#     if cpp_type not in cpp_numeric_types():
#         raise ValueError(f"{get_cpp_numeric_synonyms({cpp_type}) : not an acceptable type}")
#
#     for t in CPP_PYTHON_NUMERIC_SYNONYMS:
#         if t.cpp_type == cpp_type:
#             return t


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
    raise ValueError(f"cpp_type_to_py_array_type: unhandled type {cpp_type}")


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
