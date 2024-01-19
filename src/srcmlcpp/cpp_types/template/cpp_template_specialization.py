from __future__ import annotations

from srcmlcpp.cpp_types.decls_types.cpp_type import CppType


__all__ = ["CppTemplateSpecializationPart", "CppTemplateSpecialization"]


class CppTemplateSpecializationPart:
    """A specialization that can be applied to a template class, a template function
    or to a non template method of a template class.

        * template_name is the name of the template param, e.g. "T"
          it can be empty, in which can the specialization will be applied to
          the first non yet specialized template param
        * cpp_type is the type that will replace occurrences of the template name
    """

    cpp_type: CppType
    template_name: str = ""

    def __init__(self, cpp_type: CppType | str, template_name: str = ""):
        if isinstance(cpp_type, CppType):
            self.cpp_type = cpp_type
        elif isinstance(cpp_type, str):
            from srcmlcpp import srcmlcpp_main
            from srcmlcpp.srcmlcpp_options import SrcmlcppOptions

            dummy_options = SrcmlcppOptions()
            self.cpp_type = srcmlcpp_main.code_to_cpp_type(dummy_options, cpp_type)
        self.template_name = template_name
        # We do not support specialization types whose name is composed of multiple words,
        # such as "unsigned int". Please use "uint" or other typedefs.
        assert len(self.cpp_type.typenames) == 1

    def __str__(self):
        if len(self.template_name) > 0:
            return f"{self.template_name} -> {str(self.cpp_type)}"
        else:
            return str(self.cpp_type)


class CppTemplateSpecialization:
    specializations: list[CppTemplateSpecializationPart]

    def __init__(self, check_private_constructor: str):
        if check_private_constructor != "from_within":
            raise Exception("Please use named constructors, this constructor is private!")

    @staticmethod
    def from_type_str(cpp_type_str: str, template_name: str = "") -> CppTemplateSpecialization:
        r = CppTemplateSpecialization("from_within")
        r.specializations = [CppTemplateSpecializationPart(cpp_type_str, template_name)]
        return r

    @staticmethod
    def from_type(cpp_type: CppType, template_name: str = "") -> CppTemplateSpecialization:
        r = CppTemplateSpecialization("from_within")
        r.specializations = [CppTemplateSpecializationPart(cpp_type, template_name)]
        return r

    @staticmethod
    def from_specializations(specializations: list[CppTemplateSpecializationPart]) -> CppTemplateSpecialization:
        r = CppTemplateSpecialization("from_within")
        r.specializations = specializations
        return r
