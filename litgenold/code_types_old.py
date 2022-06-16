# from dataclasses import dataclass as _dataclass, field as _field
# from enum import Enum as _Enum
# from typing import Optional, List, Tuple
#
# import internal.code_replacements as _code_replacements
#
#
# class CppCodeType(_Enum):
#     STRUCT = "Struct"
#     FUNCTION = "Function"
#     ENUM_CPP_98 = "Enum - C++ 98"
#
#
# class CppParseException(Exception):
#     pass
#
#
# @_dataclass
# class LineNumberedItem:
#     line_number: int = 0  # starting line of the struct / enum / function,
#     # either in the whole code or inside a struct/enum
#
#
# @_dataclass
# class PydefCode(LineNumberedItem):
#     """
#     Result of the first pass of the parser:
#     Container for the code of either:
#         * the body of a struct
#         * the body of an enum
#         * the parameters of a function declaration
#     """
#
#     code_type: CppCodeType = CppCodeType.STRUCT
#     name_cpp: str = ""
#     docstring_cpp: str = ""  # the short title just one line before the struct or function declaration
#     line_end: int = 0  # end line of the struct / enum / function
#     body_code_cpp: str = ""  # the code inside the struct or enum body, or inside the function input params signature
#     return_type_cpp: str = ""  # The return type (for functions only)
#     declaration_line: str = ""  # A verbatim copy of the first declaration line
#
#     def __init__(
#         self,
#         code_type: CppCodeType,
#         name_cpp: str = "",
#         return_type_cpp: str = "",
#         declaration_line: str = "",
#     ):
#         self.code_type = code_type
#         self.name_cpp = name_cpp
#         self.return_type_cpp = return_type_cpp
#         self.declaration_line = declaration_line
#
#
# @_dataclass
# class PydefAttribute(LineNumberedItem):
#     name_cpp: str = ""
#     type_cpp: str = ""
#     default_value_cpp: str = ""
#     docstring_cpp: str = ""
#
#
# @_dataclass
# class PydefEnumCpp98Value(LineNumberedItem):
#     name_cpp: str = ""
#     # name_python cannot be inferred from name_cpp in a C++ 98 enum (i.e. not enum class)
#     # (for example in a C++ enum `ImplotCol_`, the value `ImPlotCol_Line` would be named `Line` in python)
#     name_python: str = ""
#     docstring_cpp: str = ""
#
#
# @_dataclass
# class CodeRegionComment(LineNumberedItem):
#     """
#     A CodeRegionComment is the beginning of a "code region" inside a struct or enum
#     It should look like this in the C++ header file:
#
#     `````cpp
#     //
#     // Display size and title                                                <=== This is a CodeRegionComment
#     // (the display size can differ from the image size)                     <=== It can span several lines
#     //
#
#     // Size of the displayed image (can be different from the matrix size)   <=== This is a docstring for a struct member
#     cv::Size ImageDisplaySize = cv::Size();                                       It is directly on top of the member decl
#     // Title displayed in the border
#     std::string Legend = "Image";
#     ````
#
#     """
#
#     docstring_cpp: str = ""
#
#
# @_dataclass
# class FunctionsInfos:
#     function_code: PydefCode = None
#     parameters: List[PydefAttribute] = _field(default_factory=list)
#
#     # See https://pybind11-jagerman.readthedocs.io/en/stable/advanced.html?highlight=reference#return-value-policies
#     # If you annotate a function declaration, you can set the return value lifetime policy:
#     # For example:
#     #       ````cpp
#     #       Foo& getFoo()    // return_value_policy::reference
#     #       ````
#     return_value_policy: str = ""
#
#     # Typed accessor
#     def get_parameters(self) -> List[PydefAttribute]:
#         return self.parameters
#
#     def function_name_cpp(self):
#         return self.function_code.name_cpp
#
#     def return_type_cpp(self):
#         return self.function_code.return_type_cpp
#
#
# @_dataclass
# class Variant_Attribute_Method_CodeRegion:
#     line_number: int = 0
#     code_region_comment: CodeRegionComment = None
#     attribute: PydefAttribute = None
#     enum_cpp_98_value: PydefEnumCpp98Value = None
#     method_infos: FunctionsInfos = None
#
#
# @_dataclass
# class StructInfos:
#     struct_code: PydefCode = None
#     attr_and_regions: List[Variant_Attribute_Method_CodeRegion] = _field(default_factory=list)
#
#     # Typed accessor
#     def get_attr_and_regions(self) -> List[Variant_Attribute_Method_CodeRegion]:
#         return self.attr_and_regions
#
#     def struct_name(self):
#         return self.struct_code.name_cpp
#
#
# @_dataclass
# class EnumCpp98Infos:
#     enum_code: PydefCode = None
#     attr_and_regions: List[Variant_Attribute_Method_CodeRegion] = _field(default_factory=list)
#
#     # Typed accessor
#     def get_attr_and_regions(self) -> List[Variant_Attribute_Method_CodeRegion]:
#         return self.attr_and_regions
#
#     def enum_name(self):
#         return self.enum_code.name_cpp
