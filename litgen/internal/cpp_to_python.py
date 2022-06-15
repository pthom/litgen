import pathlib
from dataclasses import dataclass  # noqa
from litgen import CodeStyleOptions
from litgen.internal import code_replacements, code_utils
from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_main

"""
Code utilities for transcription from C++ to Python
"""


def _filename_with_n_parent_folders(filename: str, n: int):
    path = pathlib.Path(filename)
    index_start = len(path.parts) - 1 - n
    if index_start < 0:
        index_start = 0
    r = "/".join(path.parts[index_start:])
    return r


def _info_original_location(
    cpp_element: CppElement, options: CodeStyleOptions, comment_token: str
):

    if not options.original_location_flag_show:
        return ""

    nb_folders = options.original_location_nb_parent_folders
    header_file = srcml_main.srcml_main_context().current_parsed_file
    header_file = _filename_with_n_parent_folders(header_file, nb_folders)
    if len(header_file) == 0:
        header_file = "Line"

    _i_ = options.indent_cpp_spaces()

    line = cpp_element.start().line
    r = f"{_i_}{comment_token} {header_file}:{line}"
    return r


def info_original_location_cpp(cpp_element: CppElement, options: CodeStyleOptions):
    return _info_original_location(cpp_element, options, "//")


def info_original_location_python(cpp_element: CppElement, options: CodeStyleOptions):
    return _info_original_location(cpp_element, options, "#")


def _comment_apply_replacements(comment: str, options: CodeStyleOptions) -> str:
    """Make some replacements in a C++ comment in order to adapt it to python
    (strip empty lines, remove API markers, apply replacements)
    """
    lines = comment.split("\n")
    if options.python_strip_empty_comment_lines:
        lines = code_utils.strip_empty_lines_in_list(lines)
    if len(lines) == 0:
        return ""

    last_line = lines[-1].strip()
    if last_line in options.srcml_options.api_suffixes:
        lines = lines[:-1]  # noqa
        lines = code_utils.strip_empty_lines_in_list(lines)

    if len(lines) == 0:
        return ""

    comment = "\n".join(lines)
    comment = code_replacements.apply_code_replacements(
        comment, options.code_replacements
    )

    return comment


def docstring_lines(
    cpp_element_c: CppElementAndComment, options: CodeStyleOptions
) -> List[str]:
    """Return the comment of a CppElement under the form of a docstring, such as the one you are reading.
    Some replacements will be applied (for example true -> True, etc)
    """

    docstring = cpp_element_c.cpp_element_comments.full_comment()
    docstring = _comment_apply_replacements(docstring, options)

    if len(docstring) == 0:
        return []

    lines = docstring.split("\n")

    r = []  # noqa
    r.append(f'''"""''' + lines[0])
    r += lines[1:]

    if len(r) == 1:
        r[0] += '''"""'''
    else:
        r.append('"""')

    return r


def python_shall_place_comment_at_end_of_line(
    cpp_element_c: CppElementAndComment, options: CodeStyleOptions
) -> bool:
    eol_comment = _comment_apply_replacements(
        cpp_element_c.cpp_element_comments.comment_end_of_line, options
    )
    p_comment = _comment_apply_replacements(
        cpp_element_c.cpp_element_comments.comment_on_previous_lines, options
    )
    return len(eol_comment) > 0 and len(p_comment) == 0


def python_comment_end_of_line(
    cpp_element_c: CppElementAndComment, options: CodeStyleOptions
) -> str:
    eol_comment = _comment_apply_replacements(
        cpp_element_c.cpp_element_comments.comment_end_of_line, options
    )
    return eol_comment


def python_comment_previous_lines(
    cpp_element_c: CppElementAndComment, options: CodeStyleOptions
) -> List[str]:
    """See comment below"""
    # Returns the comment of a CppElement under the form of a python comment, such as the one you are reading.
    # Some replacements will be applied (for example true -> True, etc)

    comment = cpp_element_c.cpp_element_comments.full_comment()
    if isinstance(cpp_element_c, CppComment):
        comment = cpp_element_c.comment

    comment = _comment_apply_replacements(comment, options)

    if len(comment) == 0:
        return []

    lines = comment.split("\n")
    lines = list(map(lambda s: "# " + s, lines))

    return lines


def docstring_python_one_line(title_cpp: str, options: CodeStyleOptions) -> str:
    """Formats a docstring on one cpp line. Used only in cpp bindings code"""
    return code_utils.format_cpp_comment_on_one_line(
        _comment_apply_replacements(title_cpp, options)
    )


def type_to_python(type_cpp: str, options: CodeStyleOptions) -> str:
    return code_replacements.apply_code_replacements(
        type_cpp, options.code_replacements
    ).strip()


def var_name_to_python(var_name: str, options: CodeStyleOptions) -> str:  # noqa
    return code_utils.to_snake_case(var_name)


def decl_python_var_name(cpp_decl: CppDecl, options: CodeStyleOptions):
    var_cpp_name = cpp_decl.name_without_array()
    var_python_name = var_name_to_python(var_cpp_name, options)
    return var_python_name


def decl_python_value(cpp_decl: CppDecl, options: CodeStyleOptions):
    value_cpp = cpp_decl.init
    value_python = code_replacements.apply_code_replacements(
        value_cpp, options.code_replacements
    )
    return value_python


def function_name_to_python(
    function_name: str, options: CodeStyleOptions
) -> str:  # noqa
    return code_utils.to_snake_case(function_name)


def is_float_str(s: str) -> bool:
    try:
        _ = float(s)
    except ValueError:
        return False
    return True


def default_value_to_python(default_value_cpp: str, options: CodeStyleOptions) -> str:
    r = code_replacements.apply_code_replacements(
        default_value_cpp, options.code_replacements
    )

    # Handle float numbers like 1.0f
    if len(r) >= 2 and r[-1] == "f":
        if is_float_str(r[:-1]):
            return r[:-1]

    return r


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
    CppPythonTypesSynonyms("uint8_t", "int"),
    CppPythonTypesSynonyms("int8_t", "int"),
    CppPythonTypesSynonyms("uint16_t", "int"),
    CppPythonTypesSynonyms("int16_t", "int"),
    CppPythonTypesSynonyms("uint32_t", "int"),
    CppPythonTypesSynonyms("int32_t", "int"),
    CppPythonTypesSynonyms("uint64_t", "int"),
    CppPythonTypesSynonyms("int64_t", "int"),
]


def cpp_numeric_types():
    r = []
    for t in CPP_PYTHON_NUMERIC_SYNONYMS:
        r.append(t.cpp_type)
    return r


def is_cpp_type_immutable_for_python(cpp_type: str):
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
        if not is_cpp_type_immutable_for_python(cpp_type):
            raise TypeError(
                f"BoxedImmutablePythonType({cpp_type}) is seemingly not immutable"
            )
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
        pydef_code = generate_code.generate_pydef(
            struct_code, options, add_boxed_types_definitions=False
        )
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
        options_no_api = copy.deepcopy(options)
        options_no_api.srcml_options.api_suffixes = []
        options_no_api.srcml_options.functions_api_prefixes = []
        r = ""
        for cpp_type in BoxedImmutablePythonType.static_list_of_instantiated_type:
            boxed_type = BoxedImmutablePythonType(cpp_type)
            r += boxed_type._binding_code(options_no_api)
        return r


"""
In python and numpy we have the following correspondence:

Given a py::array, we can get its inner type with a char identifier like this: 
    char array_type = array.dtype().char_();

Here is the table of correspondences:
"""
_PY_ARRAY_TYPE_TO_CPP_TYPE = {
    "B": "uint8_t",
    "b": "int8_t",
    "H": "uint16_t",
    "h": "int16_t",
    "I": "uint32_t",
    "i": "int32_t",
    "L": "uint64_t",
    "l": "int64_t",
    "f": "float",
    "d": "double",
    "g": "long double",
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
        return value_name[len(enum_name) + 1 :]
    elif value_name.upper().startswith(enum_name.upper()):
        return value_name[len(enum_name) :]
    else:
        return value_name


def enum_value_name_to_python(
    enum: CppEnum, enum_element: CppDecl, options: CodeStyleOptions
) -> str:
    value_name = enum_element.name_without_array()

    if options.enum_flag_remove_values_prefix and enum.type != "class":
        value_name_no_prefix = _enum_remove_values_prefix(enum.name, value_name)
        if len(value_name_no_prefix) == 0:
            value_name_no_prefix = value_name
        if value_name_no_prefix[0].isdigit():
            value_name_no_prefix = "_" + value_name_no_prefix
        value_name = value_name_no_prefix

    r = var_name_to_python(value_name, options)
    return r


def enum_element_is_count(
    enum: CppEnum, enum_element: CppDecl, options: CodeStyleOptions
) -> bool:
    if not options.enum_flag_skip_count:
        return False

    is_class_enum = enum.type == "class"
    value_name = enum_element.name_without_array()

    if not code_utils.var_name_looks_like_size_name(
        value_name, options.buffer_size_names
    ):
        return False

    if is_class_enum:
        return True
    else:
        has_enum_name_part = code_utils.var_name_contains_word(
            value_name.lower(), enum.name.lower()
        )
        return has_enum_name_part


def looks_like_size_param(param_c: CppParameter, options: CodeStyleOptions):
    r = code_utils.var_name_looks_like_size_name(
        param_c.decl.name_without_array(), options.buffer_size_names
    )
    return r
