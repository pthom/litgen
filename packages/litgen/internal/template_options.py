from __future__ import annotations
from typing import List
from dataclasses import dataclass
from enum import Enum


class TemplateNamingScheme(Enum):
    snake_prefix = 0  # MyClass<int> will be named int_MyClass
    snake_suffix = 1  # MyClass<int> will be named MyClass_int
    camel_case_prefix = 2  # MyClass<int> will be named IntMyClass
    camel_case_suffix = 3  # MyClass<int> will be named MyClassInt
    nothing = 4  # Do not neither suffix nor prefix (only possible for functions, not classes)

    @staticmethod
    def apply(scheme: TemplateNamingScheme, class_or_function_name: str, type_name: str) -> str:
        type_name = type_name.replace(" ", "_").replace("std::", "").replace("::", "_")
        camel_case_type_name = type_name[:1].upper() + type_name[1:]

        r = ""
        if scheme == TemplateNamingScheme.camel_case_suffix:
            r = class_or_function_name + camel_case_type_name
        elif scheme == TemplateNamingScheme.camel_case_prefix:
            r = camel_case_type_name + class_or_function_name
        elif scheme == TemplateNamingScheme.snake_suffix:
            r = class_or_function_name + "_" + type_name
        elif scheme == TemplateNamingScheme.snake_prefix:
            r = type_name + "_" + class_or_function_name
        elif scheme == TemplateNamingScheme.nothing:
            r = class_or_function_name
        assert len(r) > 0
        return r


@dataclass
class _TemplateSpecializationSpec:
    name_regex: str
    cpp_types_list: List[str]
    naming_scheme: TemplateNamingScheme


class TemplateFunctionsOptions:
    specs: List[_TemplateSpecializationSpec]

    def __init__(self) -> None:
        self.specs = []

    def add_specialization(
        self,
        function_name_regex: str,
        cpp_types_list: List[str],
        naming_scheme: TemplateNamingScheme = TemplateNamingScheme.nothing,
    ) -> None:
        spec = _TemplateSpecializationSpec(function_name_regex, cpp_types_list, naming_scheme)
        self.specs.append(spec)

    def add_ignore(self, function_name_regex: str) -> None:
        spec = _TemplateSpecializationSpec(function_name_regex, [], TemplateNamingScheme.nothing)
        self.specs.append(spec)


class TemplateClassOptions:
    specs: List[_TemplateSpecializationSpec]

    def __init__(self) -> None:
        self.specs = []

    def add_specialization(
        self,
        class_name_regex: str,
        cpp_types_list: List[str],
        naming_scheme: TemplateNamingScheme = TemplateNamingScheme.camel_case_suffix,
    ) -> None:
        assert naming_scheme != TemplateNamingScheme.nothing  # Specialized class names must be different in Python
        spec = _TemplateSpecializationSpec(class_name_regex, cpp_types_list, naming_scheme)
        self.specs.append(spec)

    def add_ignore(self, class_name_regex: str) -> None:
        spec = _TemplateSpecializationSpec(class_name_regex, [], TemplateNamingScheme.nothing)
        self.specs.append(spec)
