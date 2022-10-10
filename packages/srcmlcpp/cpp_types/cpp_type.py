from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import List, Optional

from codemanip import code_utils

from srcmlcpp.cpp_types.cpp_element import CppElement
from srcmlcpp.cpp_types.cpp_template import TemplateSpecialization
from srcmlcpp.srcml_wrapper import SrcmlWrapper


@dataclass
class CppType(CppElement):
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
    typenames: List[str]

    # specifiers: a list of possible specifiers
    # Acceptable specifiers: const, inline, virtual, extern, constexpr, etc.
    #
    # Important:
    # if you filled SrcmlOptions.functions_api_prefixes, then those prefixes will be mentioned
    #  as specifiers for the return type of the functions.
    specifiers: List[str]

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"], ["..."]
    modifiers: List[str]

    # template arguments types i.e ["int"] for vector<int>
    # (this will not be filled: see note about composed types)
    # argument_list: List[str]

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element)
        self.typenames: List[str] = []
        self.specifiers: List[str] = []
        self.modifiers: List[str] = []

    @staticmethod
    def authorized_modifiers() -> List[str]:
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
            raise ValueError("I cannot handle more than two `const` occurrences in a type!")

        specifiers = copy.copy(self.specifiers)
        if nb_const == 2:
            # remove the last const and handle it later
            specifier_r: List[str] = list(reversed(specifiers))
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
        return "const" in self.specifiers

    def is_static(self) -> bool:
        return "static" in self.specifiers

    def is_raw_pointer(self) -> bool:
        return "*" in self.modifiers

    def is_void(self) -> bool:
        return self.typenames == ["void"] and len(self.specifiers) == 0

    def is_inferred_type(self) -> bool:
        return self.typenames == ["auto"]

    def with_specialized_template(self, template_specs: TemplateSpecialization) -> Optional[CppType]:
        """Returns a new type where "template_name" is replaced by "cpp_type"
        Returns None if this type does not use "template_name"
        """
        import re

        was_changed = False
        new_type = copy.deepcopy(self)
        for i in range(len(new_type.typenames)):
            for template_spec in template_specs.specializations:
                assert len(template_spec.cpp_type.typenames) == 1
                template_spec_type = template_spec.cpp_type.typenames[0]
                if new_type.typenames[i] == template_spec.template_name:
                    was_changed = True
                    new_type.typenames[i] = template_spec_type
                    new_type.specifiers += template_spec.cpp_type.specifiers
                    new_type.modifiers += template_spec.cpp_type.modifiers
                else:
                    new_typename, nb_sub = re.subn(
                        rf"\b{template_spec.template_name}\b", template_spec_type, new_type.typenames[i]
                    )
                    if nb_sub > 0:
                        was_changed = True
                        new_type.typenames[i] = new_typename
                        new_type.specifiers += template_spec.cpp_type.specifiers
                        new_type.modifiers += template_spec.cpp_type.modifiers

        if was_changed:
            return new_type
        else:
            return None

    def __str__(self) -> str:
        return self.str_code()
