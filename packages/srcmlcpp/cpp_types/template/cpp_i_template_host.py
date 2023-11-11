from __future__ import annotations

from srcmlcpp.cpp_types.base import CppElementComments
from srcmlcpp.cpp_types.decls_types.cpp_type import CppType
from srcmlcpp.cpp_types.template.cpp_template import CppTemplate
from srcmlcpp.cpp_types.template.cpp_template_specialization import CppTemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppITemplateHost"]


class CppITemplateHost:
    """
    Interface added to templatable classes: CppStruct (+CppClass) and CppFunctionDecl (+CppFunction)
    """

    _template: CppTemplate
    specialized_template_params: list[CppType]  # Will only be filled after calling with_specialized_template

    def __init__(self, _element: SrcmlWrapper, _cpp_element_comments: CppElementComments) -> None:
        self._init_template_host()

    @property
    def template(self) -> CppTemplate:
        return self._template

    @template.setter
    def template(self, value: CppTemplate) -> None:
        # We can't call self.fill_children_parents() from here !
        self._template = value

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

    def _store_template_specs(self, template_specs: CppTemplateSpecialization) -> None:
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
        from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
        from srcmlcpp.cpp_types.functions.cpp_function import CppFunctionDecl

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

        r = ""
        if len(self.specialized_template_params) == 0:
            r = f"template<{template_params_str}> "
        else:
            if isinstance(self, CppFunctionDecl):
                r = f"template</*{template_params_str}*/> "
            elif isinstance(self, CppStruct):
                r = f"/*template<{template_params_str}>*/ "

        return r
