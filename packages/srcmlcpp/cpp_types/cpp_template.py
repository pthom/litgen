from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union

from srcmlcpp.cpp_types.cpp_element import (
    CppElement,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.cpp_types.cpp_parameter import CppParameterList
from srcmlcpp.cpp_types.cpp_type import CppType
from srcmlcpp.srcml_wrapper import SrcmlWrapper


@dataclass
class CppTemplate(CppElement):
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """

    parameter_list: CppParameterList

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element)
        self.parameter_list = CppParameterList(element)

    def str_code(self) -> str:
        typelist = [param.str_template_type() for param in self.parameter_list.parameters]
        typelist_str = ", ".join(typelist)
        params_str = f"template<{typelist_str}> "
        return params_str

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "parameter_list"):
            self.parameter_list.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)

    def __str__(self) -> str:
        return self.str_code()


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


class ICppTemplateHost:
    """
    Interface added to templatable classes: CppStruct (+CppClass) and CppFunctionDecl (+CppFunction)
    """

    template: CppTemplate
    specialized_template_params: List[CppType]  # Will only be filled after calling with_specialized_template

    def __init__(self, _element: SrcmlWrapper, _cpp_element_comments: CppElementComments) -> None:
        self._init_template_host()

    def _init_template_host(self) -> None:
        # self.template is not set by default. This denotes that the class of function is not a template
        self.specialized_template_params = []

    def is_template(self) -> bool:
        return hasattr(self, "template")

    def is_template_partially_specialized(self) -> bool:
        return self.is_template() and not self.is_template_fully_specialized()

    def is_template_fully_specialized(self) -> bool:
        if not self.is_template():
            return False
        nb_params = len(self.template.parameter_list.parameters)
        nb_inst = len(self.specialized_template_params)
        return nb_inst == nb_params

    def str_template_specialization(self) -> str:
        """Returns <int, double> if there is a specialization on (int, double). Return "" if no specialization"""
        if len(self.specialized_template_params) > 0:
            instantiated_params = ", ".join([str(param) for param in self.specialized_template_params])
            return f"<{instantiated_params}>"
        else:
            return ""

    def _store_template_specs(self, template_specs: TemplateSpecialization) -> None:
        for template_spec in template_specs.specializations:
            if len(template_spec.template_name) == 0:
                assert self.is_template()
                nb_remaining_template_to_instantiate = len(self.template.parameter_list.parameters) - len(
                    self.specialized_template_params
                )
                assert nb_remaining_template_to_instantiate > 0
                idx_template = len(self.specialized_template_params)
                template_spec.template_name = self.template.parameter_list.parameters[idx_template].template_name
                self.specialized_template_params.append(template_spec.cpp_type)

    def str_template(self) -> str:
        from srcmlcpp.cpp_types.cpp_class import CppStruct
        from srcmlcpp.cpp_types.cpp_function import CppFunctionDecl

        if not hasattr(self, "template"):
            return ""
        if len(self.template.parameter_list.parameters) == 0:
            return ""

        template_params_strs = []
        for i in range(len(self.template.parameter_list.parameters)):
            template_parameter = self.template.parameter_list.parameters[i]
            template_type_and_name = template_parameter.template_type + " " + template_parameter.template_name
            if i < len(self.specialized_template_params):
                template_instantiation = self.specialized_template_params[i]
                template_params_strs.append(f"{template_type_and_name}={template_instantiation}")
            else:
                template_params_strs.append(template_type_and_name)

        template_params_str = ", ".join(template_params_strs)

        if len(self.specialized_template_params) == 0:
            r = f"template<{template_params_str}> "
        else:
            if isinstance(self, CppFunctionDecl):
                r = f"template</*{template_params_str}*/> "
            elif isinstance(self, CppStruct):
                r = f"/*template<{template_params_str}>*/ "

        return r
