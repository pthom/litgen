from dataclasses import dataclass as _dataclass, field as _field
from enum import Enum as _Enum
from typing import Optional, List, Tuple

from options import CodeStyleOptions

import internal.code_replacements as _code_replacements

class CppCodeType(_Enum):
    STRUCT = "Struct"
    FUNCTION = "Function"
    ENUM_CPP_98 = "Enum - C++ 98"


class CppParseException(Exception):
    pass


@_dataclass
class PydefCode:
    """
    Container for the code of either:
        * the body of a struct
        * the body of an enum
        * the parameters of a function declaration
    """
    code_type: CppCodeType
    name_cpp: str = ""
    title_cpp: str = ""          # the short title just one line before the struct or function declaration
    line_start: int = 0          # starting line of the struct / enum / function in the whole code
    line_end: int = 0            # end line of the struct / enum / function
    body_code_cpp: str = ""      # the code inside the struct or enum body, or inside the function input params signature
    return_type_cpp: str = ""    # The return type (for functions only)

    def __init__(self, code_type: CppCodeType, name_cpp: str = "", return_type_cpp: str = ""):
        self.code_type = code_type
        self.name_cpp = name_cpp
        self.return_type_cpp = return_type_cpp

    def title_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.title_cpp, options.code_replacements)

    def return_type_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.return_type_cpp, options.code_replacements)



@_dataclass
class PydefAttribute:
    name_cpp: str = ""
    type_cpp: str = ""
    default_value_cpp: str = ""
    comment_cpp: str = ""
    line_number: int = 0  # from the body_code line_start

    def name_python(self):
        import code_utils
        return code_utils.to_snake_case(self.name_cpp)

    def type_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.type_cpp, options.code_replacements)

    def default_value_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.default_value_cpp, options.code_replacements)

    def comment_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.comment_cpp, options.code_replacements)

    def _default_value_cpp_str(self):
        return " = " + self.default_value_cpp if len(self.default_value_cpp) > 0 else ""

    def _default_value_python_str(self, options: CodeStyleOptions):
        return " = " + self.default_value_python(options) if len(self.default_value_python(options)) > 0 else ""

    def as_cpp_declaration_with_default_value(self):
        cpp_str = f"{self.type_cpp} {self.name_cpp}{self._default_value_cpp_str()}"
        return cpp_str

    def as_cpp_function_param(self):
        cpp_str = f"{self.name_cpp}"
        return cpp_str

    def as_python_declaration(self, options: CodeStyleOptions):
        python_str = f"{self.name_python()}: {self.type_python(options)}{self._default_value_python_str(options)}"
        return python_str


def _pydef_attributes_as_cpp_declaration_with_default_values(attrs: List[PydefAttribute]) -> str:
    strs = map(lambda attr: attr.as_cpp_declaration_with_default_value(), attrs)
    return ", ".join(strs)


def _pydef_attributes_as_types_only(attrs: List[PydefAttribute]) -> str:
    strs = map(lambda attr: attr.type_cpp, attrs)
    return ", ".join(strs)


def pydef_attributes_as_cpp_function_params(attrs: List[PydefAttribute]) -> str:
    strs = map(lambda attr: attr.as_cpp_function_param(), attrs)
    return ", ".join(strs)


def _pydef_attributes_as_python_declaration(attrs: List[PydefAttribute], options: CodeStyleOptions):
    strs = map(lambda attr: attr.as_python_declaration(options), attrs)
    return ", ".join(strs)


@_dataclass
class PydefEnumCpp98Value:
    name_cpp: str = ""
    # name_python cannot be inferred from name_cpp in a C++ 98 enum (i.e. not enum class)
    # (for example in a C++ enum `ImplotCol_`, the value `ImPlotCol_Line` would be named `Line` in python)
    name_python: str = ""
    comment: str = ""
    line_number: int = 0  # from the body_code line_start


@_dataclass
class CodeRegionComment:
    """
    A CodeRegionComment is the beginning of a "code region" inside a struct or enum
    It should look like this in the C++ header file:

    `````cpp
    //
    // Display size and title                                                <=== This is a CodeRegionComment
    // (the display size can differ from the image size)                     <=== It can span several lines
    //

    // Size of the displayed image (can be different from the matrix size)   <=== This is StructAttribute.comment
    cv::Size ImageDisplaySize = cv::Size();                                   (it should fit on one line)
    // Title displayed in the border
    std::string Legend = "Image";
    ````

    """
    comment_cpp: str = ""
    line_number: int = 0

    def comment_python(self, options: CodeStyleOptions):
        return _code_replacements.apply_code_replacements(self.comment_cpp, options.code_replacements)

    def as_multiline_cpp_comment(self, indentation: int):
        lines = self.comment_cpp.split("\n")
        spacing = " " * indentation
        def process_line(line):
            return spacing + "// " + line
        lines = list(map(process_line, lines))
        return "\n".join(lines)


@_dataclass
class FunctionsInfos:
    function_code: PydefCode = None
    parameters: List[PydefAttribute] = _field(default_factory=list)

    # Typed accessor
    def get_parameters(self) -> List[PydefAttribute]:
        return self.parameters

    def function_name_cpp(self):
        return self.function_code.name_cpp

    def function_name_python(self, options: CodeStyleOptions):
        import code_utils
        return code_utils.to_snake_case(self.function_name_cpp())

    def return_type_cpp(self):
        return self.function_code.return_type_cpp

    def return_type_python(self, options: CodeStyleOptions):
        return self.function_code.return_type_python(options)

    def params_declaration_str_python(self, options: CodeStyleOptions):
        strs = [param.as_python_declaration(options) for param in self.get_parameters() ]
        return ", ".join(strs)

    def declaration_python(self, options: CodeStyleOptions) -> str:
        import code_utils
        code = ""
        code += code_utils.format_python_comment(self.function_code.title_python(options), 0) + "\n"
        code += f"def {self.function_name_cpp()}(PARAMS) -> {self.return_type_python(options)}" + "\n"
        params_str = self.params_declaration_str_python(options)
        code = code.replace("PARAMS", params_str)
        return code

@_dataclass
class Variant_Attribute_Method_CodeRegion:
    line_number: int = 0
    code_region_comment: CodeRegionComment = None
    attribute: PydefAttribute = None
    enum_cpp_98_value: PydefEnumCpp98Value = None
    method_infos: FunctionsInfos = None


@_dataclass
class StructInfos:
    struct_code: PydefCode = None
    attr_and_regions: List[Variant_Attribute_Method_CodeRegion] = _field(default_factory=list)

    # Typed accessor
    def get_attr_and_regions(self) -> List[Variant_Attribute_Method_CodeRegion]:
        return self.attr_and_regions

    def struct_name(self):
        return self.struct_code.name_cpp


@_dataclass
class EnumCpp98Infos():
    enum_code: PydefCode = None
    attr_and_regions: List[Variant_Attribute_Method_CodeRegion] = _field(default_factory=list)

    # Typed accessor
    def get_attr_and_regions(self) -> List[Variant_Attribute_Method_CodeRegion]:
        return self.attr_and_regions

    def enum_name(self):
        return self.enum_code.name_cpp


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
    raise CppParseException(f"cpp_type_to_py_array_type: unhandled type {cpp_type}")
