from __future__ import annotations

import srcmlcpp
from srcmlcpp.cpp_types import CppType
from codemanip import code_utils
from codemanip.code_replacements import RegexReplacementList

from dataclasses import dataclass


def _cpp_types_list_str_to_cpp_types(cpp_types_list_str: list[str]) -> list[CppType]:
    options = srcmlcpp.SrcmlcppOptions()
    cpp_types_list = [srcmlcpp.code_to_cpp_type(options, cpp_type_str) for cpp_type_str in cpp_types_list_str]
    return cpp_types_list


def _apply_template_naming(tpl_class_or_function_name: str, instantiated_cpp_type_str: str) -> str:
    instantiated_cpp_type_str = (
        instantiated_cpp_type_str.replace("std::", "")
        .replace("::", "_")
        .replace(" &&", "_uref")
        .replace("&&", "_uref")
        .replace(" &", "_ref")
        .replace("&", "_ref")
        .replace(" *", "_ptr")
        .replace("*", "_ptr")
        .replace(" ", "_")
    )
    r = tpl_class_or_function_name + "_" + instantiated_cpp_type_str
    return r


@dataclass
class CppTypeSynonym:
    synonym_name: str
    synonym_target: str


def _make_cpp_type_synonym_list(synomym_strs: list[str] | None) -> list[CppTypeSynonym]:
    if synomym_strs is None:
        return []
    cpp_synonyms_list: list[CppTypeSynonym] = []
    for cpp_synonyms_str in synomym_strs:
        items = cpp_synonyms_str.split("=")
        assert len(items) == 2
        syn = CppTypeSynonym(items[0], items[1])
        cpp_synonyms_list.append(syn)
    return cpp_synonyms_list


@dataclass
class _TemplateSpecializationSpec:
    name_regex: str
    cpp_types_list: list[CppType]
    add_suffix_to_function_name: bool
    cpp_types_synonyms: list[CppTypeSynonym]

    def matches_template_name(self, template_name: str) -> bool:
        r = code_utils.does_match_regex(self.name_regex, template_name)
        return r

    def handles_type_instantiation(self, cpp_type: CppType) -> bool:
        r = False
        cpp_type_str = cpp_type.str_code()
        for handled_type in self.cpp_types_list:
            if cpp_type_str == handled_type.str_code():
                r = True
        return r

    def handles_type_synonym(self, cpp_type: CppType) -> bool:
        r = False
        cpp_type_str = cpp_type.str_code()
        for synonym in self.cpp_types_synonyms:
            if cpp_type_str == synonym.synonym_name:
                r = True
        return r

    def shall_synonymize_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        cpp_tpl_name = cpp_type.template_name()
        assert cpp_tpl_name is not None
        if not self.matches_template_name(cpp_tpl_name):
            return False
        template_instantiated_unique_type = cpp_type.template_instantiated_unique_type()
        if template_instantiated_unique_type is None:
            return False
        return self.handles_type_synonym(template_instantiated_unique_type)

    def shall_specialize_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        cpp_tpl_name = cpp_type.template_name()
        assert cpp_tpl_name is not None
        if not self.matches_template_name(cpp_tpl_name):
            return False
        template_instantiated_unique_type = cpp_type.template_instantiated_unique_type()
        if template_instantiated_unique_type is None:
            return False
        return self.handles_type_instantiation(template_instantiated_unique_type)

    def shall_exclude_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        cpp_tpl_name = cpp_type.template_name()
        assert cpp_tpl_name is not None
        if not self.matches_template_name(cpp_tpl_name):
            return False
        template_instantiated_unique_type = cpp_type.template_instantiated_unique_type()
        if template_instantiated_unique_type is None:
            cpp_type.emit_warning(
                f"Excluding template type {cpp_type.str_code()} because its specialization cannot be parsed (more than one specialized type?)"
            )
            return True
        shall_exclude = not self.handles_type_instantiation(
            template_instantiated_unique_type
        ) and not self.handles_type_synonym(template_instantiated_unique_type)
        if shall_exclude:
            cpp_type.emit_warning(
                f"Excluding template type {cpp_type.str_code()} because its specialization for `{template_instantiated_unique_type.str_code()}` is not handled"
            )
        return shall_exclude

    def specialized_type_python_name(self, cpp_type: CppType, type_replacements: RegexReplacementList) -> str | None:
        if not self.shall_specialize_type(cpp_type) and not self.shall_synonymize_type(cpp_type):
            return None
        cpp_tpl_name = cpp_type.template_name()
        assert cpp_tpl_name is not None
        template_instantiated_unique_type = cpp_type.template_instantiated_unique_type()
        assert template_instantiated_unique_type is not None
        template_instantiated_unique_type_str = template_instantiated_unique_type.str_code()
        name = _apply_template_naming(cpp_tpl_name, template_instantiated_unique_type_str)
        name = type_replacements.apply(name)
        return name


class TemplateSpecList:
    specs: list[_TemplateSpecializationSpec]

    def __init__(self) -> None:
        self.specs = []

    def _add_specialization(
        self,
        name_regex: str,
        cpp_types_list_str: list[str],
        add_suffix_to_function_name: bool,
        cpp_types_synonyms: list[CppTypeSynonym],
    ) -> None:
        spec = _TemplateSpecializationSpec(
            name_regex=name_regex,
            cpp_types_list=_cpp_types_list_str_to_cpp_types(cpp_types_list_str),
            add_suffix_to_function_name=add_suffix_to_function_name,
            cpp_types_synonyms=cpp_types_synonyms,
        )
        self.specs.append(spec)

    def add_ignore(self, class_name_regex: str) -> None:
        spec = _TemplateSpecializationSpec(class_name_regex, [], False, [])
        self.specs.append(spec)

    def shall_specialize_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        for s in self.specs:
            if s.shall_specialize_type(cpp_type):
                return True
        return False

    def shall_synonymize_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        for s in self.specs:
            if s.shall_synonymize_type(cpp_type):
                return True
        return False

    def shall_exclude_type(self, cpp_type: CppType) -> bool:
        if not cpp_type.is_template():
            return False
        for s in self.specs:
            if s.shall_exclude_type(cpp_type):
                return True
        return False


class TemplateFunctionsOptions(TemplateSpecList):
    def __init__(self) -> None:
        super().__init__()

    def add_specialization(
        self,
        name_regex: str,  #
        cpp_types_list_str: list[str],  #
        add_suffix_to_function_name: bool,
    ) -> None:
        """Adds a specialization for a template function.

        For example, this C++ template function:
            template<class T> T foo();

        Can be specialized for int and double like this:
            options = LitgenOptions()
            options.fn_template_options.add_specialization(
                name_regex=r"^foo$,
                cpp_types_list_str=["int", "double"],
                add_suffix_to_function_name=True)

        And the generated code will be:
            def foo_int() -> int:
                pass
            def foo_double() -> float:
                pass

        The suffix (_int and _double) is optional, and governed by the add_suffix_to_function_name parameter.
        """
        super()._add_specialization(
            name_regex=name_regex,
            cpp_types_list_str=cpp_types_list_str,
            cpp_types_synonyms=[],
            add_suffix_to_function_name=add_suffix_to_function_name,
        )

    def specialized_function_python_name(self, function_name: str, cpp_type: CppType) -> str | None:
        for s in self.specs:
            matches_name = code_utils.does_match_regex(s.name_regex, function_name)
            matches_type = s.handles_type_instantiation(cpp_type) or s.handles_type_synonym(cpp_type)
            if matches_name and matches_type:
                if s.add_suffix_to_function_name:
                    r = _apply_template_naming(function_name, cpp_type.str_code())
                    return r
                else:
                    return function_name
        return None


class TemplateClassOptions(TemplateSpecList):
    def __init__(self) -> None:
        super().__init__()

    def add_specialization(
        self, name_regex: str, cpp_types_list_str: list[str], cpp_synonyms_list_str: list[str] | None = None
    ) -> None:
        """Adds specializations for a template class:
             - name_regex is a regex that should match the name of the template class.
             - cpp_types_list_str is a list of C++ types for which a specialization will be emitted.
             - cpp_synonyms_list_str is a list of C++ type synonyms for which a python synonym should be emitted, e.g.
                cpp_synonyms_list_str=["MyInt=int", "MyDouble=double"]

        For example, given the C++ code:
            template<typename T> struct MyData { T data; };
            void Foo(MyData<MyInt> xs);
        And the options:
            options.class_template_options.add_specialization(
                name_regex="MyData",
                cpp_types_list_str=["int"],
                cpp_synonyms_list_str=["MyInt=int"]
            )

        Then, these python classes and synonyms will be emitted:
            class MyData_int:  # Python specialization for MyData<int>
                data: int
                def __init__(self, data: int = int()) -> None:
                    pass
            MyData_MyInt = MyData_int

        And the python signature of Foo will be:
            def foo(xs: MyData_MyInt) -> None:
                pass

        """
        super()._add_specialization(
            name_regex=name_regex,
            cpp_types_list_str=cpp_types_list_str,
            cpp_types_synonyms=_make_cpp_type_synonym_list(cpp_synonyms_list_str),
            add_suffix_to_function_name=False,
        )

    def specialized_type_python_default_value(
        self, cpp_default_value_str: str, type_replacements: RegexReplacementList
    ) -> str | None:
        if "<" not in cpp_default_value_str:
            return None
        has_paren = "(" in cpp_default_value_str and ")" in cpp_default_value_str
        has_accolades = "{" in cpp_default_value_str and "}" in cpp_default_value_str
        if not has_paren and not has_accolades:
            return None

        if has_accolades:
            index_paren = cpp_default_value_str.index("{")
        else:
            index_paren = cpp_default_value_str.index("(")

        cpp_default_value_type_supposed = cpp_default_value_str[0:index_paren]
        cpp_default_value_params = cpp_default_value_str[index_paren:]
        if has_accolades:
            cpp_default_value_params = cpp_default_value_params.replace("{", "(").replace("}", ")")

        specialized_type_python_name_str = self.specialized_type_python_name_str(
            cpp_default_value_type_supposed, type_replacements
        )
        if specialized_type_python_name_str is None:
            return None
        r = specialized_type_python_name_str + cpp_default_value_params
        return r

    def specialized_type_python_name_str(
        self, cpp_type_str: str, type_replacements: RegexReplacementList
    ) -> str | None:
        if "<" not in cpp_type_str:
            return None
        options = srcmlcpp.SrcmlcppOptions()
        try:
            cpp_type2 = srcmlcpp.code_to_cpp_type(options, cpp_type_str)
        except srcmlcpp.SrcmlcppException:
            return None
        return self.specialized_type_python_name(cpp_type2, type_replacements)

    def specialized_type_python_name(self, cpp_type: CppType, type_replacements: RegexReplacementList) -> str | None:
        if not self.shall_specialize_type(cpp_type) and not self.shall_synonymize_type(cpp_type):
            return None
        for s in self.specs:
            if s.shall_specialize_type(cpp_type) or s.shall_synonymize_type(cpp_type):
                return s.specialized_type_python_name(cpp_type, type_replacements)
        return None  # We should never get here!
