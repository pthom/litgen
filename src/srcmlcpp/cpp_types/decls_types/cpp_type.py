from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

from codemanip import code_utils

from srcmlcpp.cpp_types.base import CppElementAndComment, CppElementComments
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope
from srcmlcpp.srcml_wrapper import SrcmlWrapper


if TYPE_CHECKING:
    from srcmlcpp.cpp_types.template.cpp_template_specialization import CppTemplateSpecialization


__all__ = ["CppType"]


@dataclass
class CppType(CppElementAndComment):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note about composed types:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """

    # The field typenames can be:
    #   - simple: ["int"]
    #   - composed of several names, for example: ["unsigned", "long", "long"]
    #   - ["auto"] for inferred types
    #   - ["std::vector<int>"] for complex types (for example)
    typenames: list[str]

    # specifiers: a list of possible specifiers
    # Acceptable specifiers: const, inline, virtual, extern, constexpr, etc.
    #
    # Important:
    # if you filled SrcmlcppOptions.functions_api_prefixes, then those prefixes will be mentioned
    #  as specifiers for the return type of the functions.
    specifiers: list[str]

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"], ["..."]
    modifiers: list[str]

    # template arguments types i.e ["int"] for vector<int>
    # (this will not be filled: see note about composed types)
    # argument_list: List[str]

    def __init__(self, element: SrcmlWrapper) -> None:
        empty_comments = CppElementComments()
        super().__init__(element, empty_comments)
        self.typenames: list[str] = []
        self.specifiers: list[str] = []
        self.modifiers: list[str] = []

    @staticmethod
    def authorized_modifiers() -> list[str]:
        return ["*", "&", "&&", "..."]

    def str_return_type(self, remove_api_prefix: bool = True) -> str:
        # Remove unwanted specifiers
        # Possible specifiers : "const" "inline" "static" "virtual" "extern" "constexpr"
        # "inline", "virtual", "extern" and "static" do not change the return type
        specifiers = copy.copy(self.specifiers)
        unwanted_specifiers = ["inline", "virtual", "extern", "static"]
        for unwanted_specifier in unwanted_specifiers:
            if unwanted_specifier in self.specifiers:
                specifiers.remove(unwanted_specifier)
        specifiers_str = code_utils.join_remove_empty(" ", specifiers)

        # Handle const
        nb_const = self.specifiers.count("const")
        assert nb_const <= 1

        # Handle typenames with possible auto
        if len(self.typenames) > 1 and self.typenames[0] == "auto":
            name = " ".join(self.typenames[1:])
        else:
            name = " ".join(self.typenames)

        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)
        strs = [specifiers_str, name, modifiers_str]
        return_type_str = code_utils.join_remove_empty(" ", strs)

        if remove_api_prefix:
            for api_prefix in self.options.functions_api_prefixes_list():
                if return_type_str.startswith(api_prefix):
                    return_type_str = return_type_str[len(api_prefix) :].lstrip()

        return return_type_str

    def str_code(self) -> str:
        nb_const = self.specifiers.count("const")

        if nb_const > 2:
            raise ValueError("CppType.str_code() cannot handle more than two `const` occurrences in a type!")

        specifiers = copy.copy(self.specifiers)
        if nb_const == 2:
            # remove the last const and handle it later
            specifier_r: list[str] = list(reversed(specifiers))
            specifier_r.remove("const")
            specifiers = list(reversed(specifier_r))

        specifiers_str = code_utils.join_remove_empty(" ", specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        name = " ".join(self.typenames)

        name_and_arg = name
        strs = [specifiers_str, name_and_arg, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)

        if nb_const == 2:
            r += " const"

        return r

    def name_without_modifier_specifier(self) -> str:
        name = " ".join(self.typenames)
        return name

    def is_const(self) -> bool:
        return "const" in self.specifiers or "constexpr" in self.specifiers

    def is_reference(self) -> bool:
        return "&" in self.modifiers

    def is_static(self) -> bool:
        return "static" in self.specifiers

    def is_raw_pointer(self) -> bool:
        return "*" in self.modifiers

    def is_void(self) -> bool:
        return self.typenames == ["void"] and len(self.specifiers) == 0 and len(self.modifiers) == 0

    def is_inferred_type(self) -> bool:
        return self.typenames == ["auto"]

    def is_template(self) -> bool:
        joined_typenames = " ".join(self.typenames)
        r = "<" in joined_typenames and ">" in joined_typenames
        return r

    def template_name(self) -> str | None:
        if not self.is_template():
            return None
        joined_typenames = " ".join(self.typenames)
        r = joined_typenames[: joined_typenames.index("<")]
        return r

    def template_instantiated_unique_type(self) -> CppType | None:
        """Will return the instantiated type when it is a template on *only one* type
        cpp_type = srcmlcpp_main.code_to_cpp_type(options, "int")
        assert cpp_type.template_instantiated_type() is None

        cpp_type = srcmlcpp_main.code_to_cpp_type(options, "std::vector<int>")
        assert cpp_type.template_instantiated_type().str_code() == "int"

        cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::vector<std::pair<std::string,float>>")
        assert cpp_type.template_instantiated_type().str_code() == "std::pair<std::string,float>"

        cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::map<int, double>")
        assert cpp_type.template_instantiated_type() is None
        """
        import srcmlcpp.srcmlcpp_main

        if not self.is_template():
            return None
        joined_typenames = " ".join(self.typenames)
        start = joined_typenames.index("<")
        end = joined_typenames.rindex(">")
        tpl_type_str = joined_typenames[start + 1 : end]
        options = srcmlcpp.SrcmlcppOptions()
        try:
            tpl_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, tpl_type_str)
        except srcmlcpp.SrcmlcppException:
            return None
        return tpl_type

    def with_specialized_template(self, template_specs: CppTemplateSpecialization) -> CppType | None:
        """Returns a new type where "template_name" is replaced by "cpp_type"
        Returns None if this type does not use "template_name"
        """
        import re

        was_changed = False
        new_type = copy.deepcopy(self)
        for i in range(len(new_type.typenames)):
            for template_spec in template_specs.specializations:
                assert len(template_spec.cpp_type.typenames) == 1
                template_spec_type = template_spec.cpp_type.str_code()
                if new_type.typenames[i] == template_spec.template_name:
                    was_changed = True
                    new_type.typenames[i] = template_spec_type
                else:
                    new_typename, nb_sub = re.subn(
                        rf"\b{template_spec.template_name}\b", template_spec_type, new_type.typenames[i]
                    )
                    if nb_sub > 0:
                        was_changed = True
                        new_type.typenames[i] = new_typename

        if was_changed:
            return new_type
        else:
            return None

    def with_qualified_types(self, current_scope: CppScope | None = None) -> CppType:
        """Returns a possibly new fully qualified type, by searching for matching types in the full CppUnit root tree
        For example, if
                self.typenames = ["MyStruct"]
            and
                current_caller_scope = Ns::Inner
            and there is a type named Ns::MyStruct in the CppUnit root tree
        then, we will return Ns::MyStruct
        otherwise we will return MyStruct
        """
        if current_scope is None:
            current_scope = self.cpp_scope()

        if len(self.typenames) == 0:
            return self

        typename = " ".join(self.typenames)

        cpp_unit = self.root_cpp_unit()
        new_typename = cpp_unit._scope_identifiers.qualify_cpp_code(typename, current_scope)
        if new_typename != typename:
            new_type = copy.deepcopy(self)
            new_type.typenames = new_typename.split(" ")
            return new_type
        else:
            return self

    def with_terse_types(self, current_scope: CppScope | None = None) -> CppType:
        if current_scope is None:
            current_scope = self.cpp_scope()

        type_qualified = self.with_qualified_types()
        type_name_qualified = " ".join(type_qualified.typenames)

        from srcmlcpp.cpp_types.scope.cpp_scope_process import make_terse_code

        new_type_name = make_terse_code(type_name_qualified, current_scope.str_cpp_prefix)
        if new_type_name != " ".join(self.typenames):
            new_cpp_type = copy.deepcopy(self)
            new_cpp_type.typenames = new_type_name.split(" ")
            return new_cpp_type
        else:
            return self

    def __str__(self) -> str:
        return self.str_code()

    def __repr__(self):
        return self.str_code()
