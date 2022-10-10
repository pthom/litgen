from __future__ import annotations
from typing import List, Union

from srcmlcpp.cpp_types.decls_types.cpp_type import CppType


class TemplateSpecializationPart:
    cpp_type: CppType
    template_name: str = ""  # If empty, will be applied to the first available template param

    def __init__(self, cpp_type: Union[CppType, str], template_name: str = ""):
        if isinstance(cpp_type, CppType):
            self.cpp_type = cpp_type
        elif isinstance(cpp_type, str):
            from srcmlcpp import srcmlcpp_main
            from srcmlcpp.srcml_options import SrcmlOptions

            dummy_options = SrcmlOptions()
            self.cpp_type = srcmlcpp_main.code_to_cpp_type(dummy_options, cpp_type)
            self.template_name = template_name

        # We do not support type composed of multiple word here, such as "unsigned int".
        # Please use "uint" or other typedefs.
        assert len(self.cpp_type.typenames) == 1

    def __str__(self):
        if len(self.template_name) > 0:
            return f"{self.template_name} -> {str(self.cpp_type)}"
        else:
            return str(self.cpp_type)


class TemplateSpecialization:
    specializations: List[TemplateSpecializationPart]

    def __init__(self, check_private_constructor: str):
        if check_private_constructor != "from_within":
            raise Exception("Please use named constructors, this constructor is private!")

    @staticmethod
    def from_type_str(cpp_type_str: str, template_name: str = "") -> TemplateSpecialization:
        r = TemplateSpecialization("from_within")
        r.specializations = [TemplateSpecializationPart(cpp_type_str, template_name)]
        return r

    @staticmethod
    def from_type(cpp_type: CppType, template_name: str = "") -> TemplateSpecialization:
        r = TemplateSpecialization("from_within")
        r.specializations = [TemplateSpecializationPart(cpp_type, template_name)]
        return r

    @staticmethod
    def from_specializations(specializations: List[TemplateSpecializationPart]) -> TemplateSpecialization:
        r = TemplateSpecialization("from_within")
        r.specializations = specializations
        return r
