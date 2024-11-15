from __future__ import annotations

from dataclasses import dataclass
from typing import cast

import munch  # type: ignore

import litgen
import srcmlcpp
from codemanip import code_utils

from srcmlcpp.cpp_types import (
    CppDecl,
    CppDeclStatement,
    CppEmptyLine,
    CppStruct,
    CppType,
    CppAccessType,
    CppComment,
    CppFunctionDecl,
    CppUnprocessed,
    CppEnum,
    CppConditionMacro,
    CppClass,
    CppUnit,
    CppPublicProtectedPrivate,
    CppConstructorDecl,
    CppTemplateSpecialization,
)
from srcmlcpp.cpp_types.scope.cpp_scope import CppScopeType
from srcmlcpp.srcmlcpp_exception import SrcmlcppException
from srcmlcpp.scrml_warning_settings import WarningType

from litgen import BindLibraryType
from litgen.internal import cpp_to_python, template_options
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_enum import AdaptedEnum
from litgen.internal.adapted_types.adapted_function import AdaptedFunction
from litgen.internal.adapted_types.adapted_condition_macro import AdaptedConditionMacro
from litgen.internal.context.litgen_context import LitgenContext


@dataclass
class _AdaptedInstantiatedTemplateClasses:
    adapted_classes: list[AdaptedClass]
    stubs_synonyms_code: list[str]


@dataclass
class AdaptedClassMember(AdaptedDecl):
    """A specialization of AdaptedDecl for class member variables"""

    class_parent: AdaptedClass

    def __init__(self, lg_context: LitgenContext, decl: CppDecl, class_parent: AdaptedClass) -> None:
        self.class_parent = class_parent
        super().__init__(lg_context, decl)

    def __str__(self) -> str:
        name_cpp = self.decl_name_cpp()
        name_python = self.decl_name_python()
        if name_python != name_cpp:
            return f"AdaptedClassMember({self.decl_name_cpp()} -> {self.decl_name_python()})"
        else:
            return f"AdaptedClassMember({self.decl_name_cpp()})"

    def _is_numeric_c_array(self) -> bool:
        """Returns true if this member is a numeric C array, for example:
        int values[10];
        """
        options = self.options
        cpp_decl = self.cpp_element()
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options._member_numeric_c_array_types_list():
            return False
        shall_replace = code_utils.does_match_regex(options.member_numeric_c_array_replace__regex, cpp_decl.decl_name)
        if not shall_replace:
            return False
        if cpp_decl.c_array_size_as_int() is None:
            return False
        return True

    def _check_can_add_c_array_known_fixed_size(self) -> bool:
        options = self.options
        cpp_decl = self.cpp_element()
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options._member_numeric_c_array_types_list():
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Only numeric C Style arrays are supported
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                WarningType.LitgenClassMemberNonNumericCStyleArray,
            )
            return False

        shall_replace = code_utils.does_match_regex(options.member_numeric_c_array_replace__regex, cpp_decl.decl_name)
        if not shall_replace:
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Detected a numeric C Style array, but will not export it.
                Hint: modify `options.member_numeric_c_array_replace__regex`
                """,
                WarningType.LitgenClassMemberNumericCStyleArray_Setting,
            )
            return False

        if cpp_decl.c_array_size_as_int() is None:
            array_size_str = cpp_decl.c_array_size_as_str()
            cpp_decl.emit_warning(
                f"""
                AdaptedClassMember: Detected a numeric C Style array, but its size is not parsable.
                Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                """,
                WarningType.LitgenClassMemberNumericCStyleArray_UnparsableSize,
            )
            return False

        return True

    def check_can_publish(self) -> bool:
        """Returns true if this member can be published as a property of the class"""
        cpp_decl = self.cpp_element()

        if cpp_decl.is_bitfield():  # is_bitfield()
            cpp_decl.emit_warning(
                f"AdaptedClassMember: Skipped bitfield member {cpp_decl.decl_name}",
                WarningType.LitgenClassMemberSkipBitfield,
            )
            return False
        elif cpp_decl.is_c_array_fixed_size_unparsable():
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Can't parse the size of this array.
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                WarningType.LitgenClassMemberUnparsableSize,
            )
            return False
        elif cpp_decl.is_c_array_known_fixed_size():
            return self._check_can_add_c_array_known_fixed_size()
        elif self.options.class_template_options.shall_exclude_type(self.cpp_element().cpp_type):
            return False
        else:
            return True

    def decl_type_python(self) -> str:
        if self._is_numeric_c_array():
            return "np.ndarray"
        else:
            return super().decl_type_python()

    def decl_value_python(self) -> str:
        if self._is_numeric_c_array():
            return ""
        else:
            return super().decl_value_python()

    def comment_array(self) -> str:
        if self._is_numeric_c_array():
            array_typename = self.cpp_element().cpp_type.str_code()
            array_size = self.cpp_element().c_array_size_as_int()
            msg = f"  # ndarray[type={array_typename}, size={array_size}]"

            decl_value_python_original = super().decl_value_python()
            if len(decl_value_python_original) > 0:
                msg += " default:" + decl_value_python_original

            return msg
        else:
            return ""

    def _str_pydef_lines_numeric_array(self) -> list[str]:
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11

        qualified_struct_name = self.class_parent.cpp_element().qualified_class_name_with_specialization()
        location = self._elm_info_original_location_cpp()
        name_python = self.decl_name_python()
        name_cpp = self.decl_name_cpp()
        comment = self._elm_comment_pydef_one_line()

        array_typename = self.cpp_element().cpp_type.str_code()
        array_size = self.cpp_element().c_array_size_as_int()
        assert array_size is not None

        if self.options.bind_library == BindLibraryType.pybind11:
            template_code = f"""
                .def_property("{name_python}",{location}
                    []({qualified_struct_name} &self) -> pybind11::array
                    {{
                        auto dtype = pybind11::dtype(pybind11::format_descriptor<{array_typename}>::format());
                        auto base = pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}});
                        return pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}}, self.{name_cpp}, base);
                    }}, []({qualified_struct_name}& self) {{}},
                    "{comment}")
                """
        else:
            template_code = f"""
                .def_prop_ro("{name_python}",{location}
                    []({qualified_struct_name} &self) -> nb::ndarray<{array_typename}, nb::numpy, nb::shape<{array_size}>, nb::c_contig>
                    {{
                        return self.{name_cpp};
                    }},
                    "{comment}")
                """

        r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True)  # + "\n"
        lines = r.split("\n")
        return lines

    def _is_published_readonly(self) -> bool:
        name_cpp = self.decl_name_cpp()
        cpp_type = self.cpp_element().cpp_type
        is_readonly = False
        if cpp_type.is_const():
            is_readonly = True
        if code_utils.does_match_regex(self.options.member_readonly_by_type__regex, cpp_type.str_code()):
            is_readonly = True
        if code_utils.does_match_regex(self.options.member_readonly_by_name__regex, name_cpp):
            is_readonly = True
        return is_readonly

    def _str_pydef_lines_field(self) -> list[str]:
        qualified_struct_name = self.class_parent.cpp_element().qualified_class_name_with_specialization()
        location = self._elm_info_original_location_cpp()
        name_python = self.decl_name_python()
        name_cpp = self.decl_name_cpp()
        comment = self._elm_comment_pydef_one_line()

        cpp_type = self.cpp_element().cpp_type
        is_pybind11 = self.options.bind_library == BindLibraryType.pybind11

        pybind_definition_mode = "def_readwrite" if is_pybind11 else "def_rw"
        if self._is_published_readonly():
            pybind_definition_mode = "def_readonly" if is_pybind11 else "def_ro"
        if cpp_type.is_static():
            pybind_definition_mode += "_static"

        r = f'.{pybind_definition_mode}("{name_python}", &{qualified_struct_name}::{name_cpp}, "{comment}"){location}'
        return [r]

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    # override
    def stub_lines(self) -> list[str]:
        code_lines: list[str] = []

        if not self._elm_comment_python_shall_place_at_end_of_line():
            code_lines += self._elm_comment_python_previous_lines()

        decl_name_python = self.decl_name_python()
        decl_type_python = self.decl_type_python()

        default_value_python = self.decl_value_python()
        if len(default_value_python) > 0:
            maybe_defaultvalue_python = default_value_python
            maybe_equal = " = "
        else:
            maybe_defaultvalue_python = ""
            maybe_equal = ""

        if not self._elm_comment_python_shall_place_at_end_of_line():
            maybe_comment = ""
        else:
            maybe_comment = self._elm_comment_python_end_of_line()

        maybe_comment_array = self.comment_array()

        location = self._elm_info_original_location_python()

        cpp_type = self.cpp_element().cpp_type
        maybe_static_info = " # (C++ static member)" if self.cpp_element().cpp_type.is_static() else ""
        maybe_const_info = " # (const)" if cpp_type.is_const() else ""
        maybe_readonly_info = " # (read-only)" if (self._is_published_readonly() and not cpp_type.is_const()) else ""

        decl_template = f"{decl_name_python}: {decl_type_python}{maybe_equal}{maybe_defaultvalue_python}{maybe_comment_array}{maybe_comment}{maybe_static_info}{maybe_const_info}{maybe_readonly_info}{location}"
        code_lines += [decl_template]

        code_lines = self._elm_stub_original_code_lines_info() + code_lines
        return code_lines

    # override
    def pydef_lines(self) -> list[str]:
        if self._is_numeric_c_array():
            return self._str_pydef_lines_numeric_array()
        else:
            return self._str_pydef_lines_field()


@dataclass
class AdaptedClass(AdaptedElement):
    """AdaptedClass: an adapted CppStruct or CppClass

    @see AdaptedElement

    AdaptedClass is able to handle quite a lot of cases. Its code is separated in several logical sections:
        - Initialization and basic services
        - pydef and stub code generation
        - _cp_: (deep)copy handling
        - _tpl_: template classes handling
        - _virt_: virtual methods handling
        - _prot_: protected methods handling (when they are published)
    """

    #  ============================================================================================
    #
    #    Members
    #
    #  ============================================================================================

    # List of all public children (methods, members, inner structs, etc.)
    adapted_public_children: list[
        (
            AdaptedEmptyLine
            | AdaptedComment
            | AdaptedClassMember
            | AdaptedFunction
            | AdaptedClass
            | AdaptedEnum
            | AdaptedConditionMacro
        )
    ]
    # Protected methods, if this class is supposed to output binding for its protected methods
    adapted_protected_methods: list[AdaptedFunction]

    # template_specialization store the optional specialization of this AdaptedClass
    @dataclass
    class TemplateSpecialization:
        class_name_python: str
        cpp_type: CppType

    template_specialization: TemplateSpecialization | None = None

    #  ============================================================================================
    #
    #    Initialization
    #
    #  ============================================================================================

    def __init__(self, lg_context: LitgenContext, class_: CppStruct):
        super().__init__(lg_context, class_)
        self.adapted_public_children = []
        self._init_fill_public_children()

        self.adapted_protected_methods = []
        self._prot_fill_methods()

    def _init_add_adapted_class_member(self, cpp_decl_statement: CppDeclStatement) -> None:
        class_name = self.cpp_element().class_name

        for cpp_decl in cpp_decl_statement.cpp_decls:
            is_excluded_by_name_and_class = code_utils.does_match_regex(
                self.options.member_exclude_by_name_and_class__regex.get(class_name, ""), cpp_decl.decl_name
            )
            is_excluded_by_name = code_utils.does_match_regex(
                self.options.member_exclude_by_name__regex, cpp_decl.decl_name
            )
            is_excluded_by_type = code_utils.does_match_regex(
                self.options.member_exclude_by_type__regex, cpp_decl.cpp_type.str_code()
            )
            if not is_excluded_by_name_and_class and not is_excluded_by_name and not is_excluded_by_type:
                adapted_class_member = AdaptedClassMember(self.lg_context, cpp_decl, self)
                if adapted_class_member.check_can_publish():
                    self.adapted_public_children.append(adapted_class_member)

    def _init_add_adopted_class_function(self, cpp_function_decl: CppFunctionDecl) -> None:
        class_name = self.cpp_element().class_name

        is_excluded_by_name_and_class = code_utils.does_match_regex(
            self.options.member_exclude_by_name_and_class__regex.get(class_name, ""), cpp_function_decl.name()
        )
        if not is_excluded_by_name_and_class:
            if AdaptedFunction.init_is_function_publishable(self.options, cpp_function_decl):
                is_overloaded = cpp_function_decl.is_overloaded_method()
                self.adapted_public_children.append(AdaptedFunction(self.lg_context, cpp_function_decl, is_overloaded))

    def _init_fill_public_children(self) -> None:
        public_elements = self.cpp_element().get_elements(access_type=CppAccessType.public)
        for child in public_elements:
            try:
                if isinstance(child, CppEmptyLine):
                    self.adapted_public_children.append(AdaptedEmptyLine(self.lg_context, child))
                elif isinstance(child, CppComment):
                    self.adapted_public_children.append(AdaptedComment(self.lg_context, child))
                elif isinstance(child, CppFunctionDecl):
                    self._init_add_adopted_class_function(child)
                elif isinstance(child, CppDeclStatement):
                    self._init_add_adapted_class_member(child)
                elif isinstance(child, CppUnprocessed):
                    continue
                elif isinstance(child, CppStruct):
                    adapted_subclass = AdaptedClass(self.lg_context, child)
                    self.adapted_public_children.append(adapted_subclass)
                elif isinstance(child, CppEnum):
                    adapted_enum = AdaptedEnum(self.lg_context, child)
                    self.adapted_public_children.append(adapted_enum)
                elif isinstance(child, CppConditionMacro):
                    adapted_macro = AdaptedConditionMacro(self.lg_context, child)
                    self.adapted_public_children.append(adapted_macro)
                else:
                    child.emit_warning(
                        f"Public elements of type {child.tag()} are not supported in python conversion",
                        WarningType.LitgenClassMemberUnsupported,
                    )
            except SrcmlcppException as e:
                child.emit_warning(str(e), WarningType.LitgenClassMemberException)

    #  ============================================================================================
    #
    #    Basic services
    #
    #  ============================================================================================

    def __str__(self) -> str:
        r = f"AdaptedClass({self.cpp_element().class_name})"
        return r

    def __repr__(self) -> str:
        return self.__str__()

    # override
    def cpp_element(self) -> CppStruct:
        return cast(CppStruct, self._cpp_element)

    def class_name_python(self) -> str:
        if self.template_specialization is not None:
            return self.template_specialization.class_name_python
        r = cpp_to_python._class_name_to_python(self.options, self.cpp_element().class_name)
        return r

    #  ============================================================================================
    #
    #    _str_stub_lines: main API for code generation
    #    We override this methods from AdaptedElement
    #
    #  ============================================================================================

    # override
    def stub_lines(self) -> list[str]:
        # If this is a template class, implement as many versions
        # as mentioned in the options (see LitgenOptions.class_template_options)
        # and bail out
        if self.cpp_element().is_template_partially_specialized():
            template_instantiations = self._tpl_split_into_template_instantiations()
            if len(template_instantiations.adapted_classes) == 0:
                return []
            else:
                r: list[str] = []
                for template_instantiation in template_instantiations.adapted_classes:
                    if len(r) > 0:
                        r += ["", ""]  # 2 empty lines between classes
                    r += template_instantiation.stub_lines()

                for stub_synonym_code in template_instantiations.stubs_synonyms_code:
                    r += ["", stub_synonym_code, ""]

                if self.options.class_template_decorate_in_stub:
                    r = cpp_to_python.surround_python_code_lines(
                        r, f"template specializations for class {self.class_name_python()}"
                    )
                return r

        def str_parent_classes_python() -> str:
            parents: list[str] = []
            if not self.cpp_element().has_base_classes():
                return ""
            for _access_type, base_class in self.cpp_element().base_classes():
                class_python_scope = cpp_to_python.cpp_scope_to_pybind_scope_str(
                    self.options, base_class, include_self=True
                )
                parents.append(class_python_scope)
            if len(parents) == 0:
                return ""
            else:
                return "(" + ", ".join(parents) + ")"

        from litgen.internal.adapted_types.line_spacer import LineSpacerPython

        line_spacer = LineSpacerPython(self.options)

        class_name = self.class_name_python()

        title = f"class {class_name}{str_parent_classes_python()}:"
        if self.template_specialization is not None:
            title += f"  # Python specialization for {self.cpp_element().class_name}<{self.template_specialization.cpp_type.str_code()}>"

        title_lines = [title]
        if self.cpp_element().is_final():
            self.cpp_element().cpp_element_comments.comment_on_previous_lines += "\n"
            self.cpp_element().cpp_element_comments.comment_on_previous_lines += "(final class)"
        if len(self._cp_stub_comment()) > 0:
            self.cpp_element().cpp_element_comments.comment_on_previous_lines += "\n" + self._cp_stub_comment()

        body_lines: list[str] = []

        for element in self.adapted_public_children:
            element_lines = element.stub_lines()

            spacing_lines = line_spacer.spacing_lines(element, element_lines)
            body_lines += spacing_lines
            body_lines += element_lines

        # add named constructor (if active via options)
        if (
            not self.cpp_element().has_user_defined_constructor()
            and not self.cpp_element().has_deleted_default_constructor()
        ):
            ctor_helper = PythonNamedConstructorHelper(self)
            ctor_code = ctor_helper.stub_code()
            body_lines += ctor_code.split("\n")

        if len(self.adapted_protected_methods) > 0:
            body_lines += ["", "# <protected_methods>"]
            for element in self.adapted_protected_methods:
                element_lines = element.stub_lines()

                spacing_lines = line_spacer.spacing_lines(element, element_lines)
                body_lines += spacing_lines
                body_lines += element_lines
            body_lines += ["# </protected_methods>", ""]

        def make_iterable_code() -> str:
            flag_add = self.options.class_iterables_infos.is_class_iterable(self.class_name_python())
            if not flag_add:
                return ""

            code_template = code_utils.unindent_code(
                """
                def __iter__(self) -> Iterator[{iterator_class_name_python}]:
                {_i_}pass
                def __len__(self) -> int:
                {_i_}pass
                """,
                flag_strip_empty_lines=True,
            )

            replacements = munch.Munch()
            replacements._i_ = self.options._indent_cpp_spaces()
            replacements.iterator_class_name_python = self.options.class_iterables_infos.python_iterable_type(
                self.class_name_python()
            )
            iter_code = code_utils.process_code_template(code_template, replacements)

            return iter_code

        body_lines += make_iterable_code().splitlines()

        r = self._elm_str_stub_layout_lines(title_lines, body_lines)
        return r

    #  ============================================================================================
    #
    #    _str_pydef_lines: main API for code generation
    #    We override this methods from AdaptedElement
    #
    #  ============================================================================================

    # override
    def pydef_lines(self) -> list[str]:
        # If this is a template class, implement as many versions
        # as mentioned in the options (see LitgenOptions.class_template_options)
        # and bail out
        if self.cpp_element().is_template_partially_specialized():
            template_instantiations = self._tpl_split_into_template_instantiations()
            if len(template_instantiations.adapted_classes) == 0:
                return []
            else:
                r = []
                for template_instantiation in template_instantiations.adapted_classes:
                    r += template_instantiation.pydef_lines()
                return r

        self._prot_store_glue()
        self._virt_store_glue_override()

        options = self.options
        _i_ = options._indent_cpp_spaces()

        def is_class_or_enum(e: AdaptedElement) -> bool:
            return isinstance(e, AdaptedClass) or isinstance(e, AdaptedEnum)

        def not_is_class_or_enum(e: AdaptedElement) -> bool:
            return not (isinstance(e, AdaptedClass) or isinstance(e, AdaptedEnum))

        children_except_inner_classes = list(filter(not_is_class_or_enum, self.adapted_public_children))
        children_inner_classes = list(filter(is_class_or_enum, self.adapted_public_children))

        def make_pyclass_creation_code() -> str:
            """Return the C++ code that instantiates the class.

            Will look like:
                auto pyClassFoo =
                    py::class_<Foo>
                        (m, "Foo", "");
            """
            qualified_struct_name = self.cpp_element().qualified_class_name_with_specialization()

            # fill py::class_ additional template params (base classes, nodelete, etc)
            other_template_params_list = []
            if self.cpp_element().has_base_classes():
                base_classes = self.cpp_element().base_classes()
                for access_type, base_class in base_classes:
                    if access_type == CppAccessType.public or access_type == CppAccessType.protected:
                        other_template_params_list.append(base_class.cpp_scope_str(include_self=True))
            if self.cpp_element().has_private_destructor() and options.bind_library == BindLibraryType.pybind11:
                # nanobind does not support nodelete
                other_template_params_list.append(f"std::unique_ptr<{qualified_struct_name}, py::nodelete>")
            if self._virt_shall_override():
                scope = self.cpp_element().cpp_scope(False).str_cpp
                scope_prefix = scope + "::" if len(scope) > 0 else ""
                qualified_trampoline_name = scope_prefix + self.cpp_element().class_name + "_trampoline"
                other_template_params_list.append(qualified_trampoline_name)

            if len(other_template_params_list) > 0:
                other_template_params = ", " + ", ".join(other_template_params_list)
            else:
                other_template_params = ""

            code_template = code_utils.unindent_code(
                """
                    auto {pydef_class_var} =
                    {_i_}{py}::class_<{qualified_struct_name}{other_template_params}{maybe_shared_ptr_holder}>{location}
                    {_i_}{_i_}({pydef_class_var_parent}, "{class_name_python}"{maybe_py_is_final}{maybe_py_is_dynamic}, "{comment}")
                    """,
                flag_strip_empty_lines=True,
            )

            replacements = munch.Munch()
            replacements.py = "py" if options.bind_library == BindLibraryType.pybind11 else "nb"
            replacements._i_ = self.options._indent_cpp_spaces()
            replacements.pydef_class_var = cpp_to_python.cpp_scope_to_pybind_var_name(options, self.cpp_element())
            replacements.qualified_struct_name = qualified_struct_name
            replacements.other_template_params = other_template_params
            replacements.location = self._elm_info_original_location_cpp()
            replacements.class_name_python = self.class_name_python()
            replacements.pydef_class_var_parent = cpp_to_python.cpp_scope_to_pybind_parent_var_name(
                options, self.cpp_element()
            )

            if self.cpp_element().is_final():
                replacements.maybe_py_is_final = (
                    ", py::is_final()" if options.bind_library == BindLibraryType.pybind11 else ", nb::is_final()"
                )
            else:
                replacements.maybe_py_is_final = ""

            if code_utils.does_match_regex(self.options.class_dynamic_attributes__regex, self.cpp_element().class_name):
                if options.bind_library == BindLibraryType.pybind11:
                    replacements.maybe_py_is_dynamic = ", py::dynamic_attr()"
                else:
                    replacements.maybe_py_is_dynamic = ", nb::dynamic_attr()"
            else:
                replacements.maybe_py_is_dynamic = ""

            replacements.comment = self._elm_comment_pydef_one_line()

            if (
                code_utils.does_match_regex(options.class_held_as_shared__regex, self.cpp_element().class_name)
                and self.options.bind_library == BindLibraryType.pybind11
            ):
                replacements.maybe_shared_ptr_holder = f", std::shared_ptr<{qualified_struct_name}>"
            else:
                replacements.maybe_shared_ptr_holder = ""

            pyclass_creation_code = code_utils.process_code_template(code_template, replacements)

            return pyclass_creation_code

        def make_default_constructor_code() -> str:
            if self.cpp_element().has_deleted_default_constructor():
                return f"{_i_}// (default constructor explicitly deleted)\n"
            elif not self.cpp_element().has_user_defined_constructor():
                python_named_ctor_helper = PythonNamedConstructorHelper(self)
                return python_named_ctor_helper.pydef_code()
            else:
                return ""

        def make_public_children_code() -> str:
            r = ""
            for child in children_except_inner_classes:
                decl_code = child.str_pydef()
                r += code_utils.indent_code(decl_code, indent_str=options._indent_cpp_spaces())
            return r

        def make_inner_classes_code() -> str:
            r = ""
            if len(children_inner_classes) > 0:
                r += "\n{" + f" // inner classes & enums of {self.class_name_python()}\n"
                for child in children_inner_classes:
                    decl_code = child.str_pydef()
                    r += code_utils.indent_code(decl_code, indent_str=options._indent_cpp_spaces())
                r += "}" + f" // end of inner classes & enums of {self.class_name_python()}"
            return r

        def make_protected_methods_code() -> str:
            r = ""
            for child in self.adapted_protected_methods:
                # Temporarily change the name of the parent struct, to use the publicist class
                parent_struct = child.cpp_element().parent_struct_if_method()
                assert parent_struct is not None
                original_class_name = parent_struct.class_name
                parent_struct.class_name = self.cpp_element().class_name + "_publicist"
                decl_code = child.str_pydef()
                parent_struct.class_name = original_class_name

                r += code_utils.indent_code(decl_code, indent_str=options._indent_cpp_spaces())
            return r

        def make_copy_deepcopy_code() -> str:
            r = code_utils.indent_code(self._cp_pydef(), indent_str=self.options._indent_cpp_spaces())
            return r

        def make_iterable_code() -> str:
            flag_add = self.options.class_iterables_infos.is_class_iterable(self.class_name_python())
            if not flag_add:
                return ""

            if self.options.bind_library == BindLibraryType.pybind11:
                code_template = (
                    code_utils.unindent_code(
                        """
                    .def("__iter__", [](const {qualified_struct_name} &v) { return py::make_iterator(v.begin(), v.end()); }, py::keep_alive<0, 1>())
                    .def("__len__", [](const {qualified_struct_name} &v) { return v.size(); })
                    """,
                        flag_strip_empty_lines=True,
                    )
                    + "\n"
                )
            else:
                code_template = (
                    code_utils.unindent_code(
                        """
                    .def("__iter__", [](const {qualified_struct_name} &v) {
                            return nb::make_iterator(nb::type<{qualified_struct_name}>(), "iterator", v.begin(), v.end());
                        }, nb::keep_alive<0, 1>())
                    .def("__len__", [](const {qualified_struct_name} &v) { return v.size(); })
                    """,
                        flag_strip_empty_lines=True,
                    )
                    + "\n"
                )

            replacements = munch.Munch()
            replacements._i_ = self.options._indent_cpp_spaces()
            replacements.qualified_struct_name = self.cpp_element().qualified_class_name_with_specialization()

            iter_code = code_utils.process_code_template(code_template, replacements)
            iter_code = code_utils.indent_code(iter_code, len(options._indent_cpp_spaces()))

            return iter_code

        def make_all_children_code() -> str:
            children_code = make_default_constructor_code()
            children_code += make_public_children_code()
            children_code += make_protected_methods_code()
            children_code += make_copy_deepcopy_code()
            children_code += make_iterable_code()
            return children_code

        inner_classes_code = make_inner_classes_code()

        code = make_pyclass_creation_code()
        if len(inner_classes_code) > 0:
            pydef_class_var = cpp_to_python.cpp_scope_to_pybind_var_name(options, self.cpp_element())

            code += ";\n"
            code += inner_classes_code + "\n\n"
            code += pydef_class_var + "\n"
            code += make_all_children_code()
        else:
            code += "\n" + make_all_children_code()

        code = code + f"{_i_};"

        lines = code.split("\n")
        return lines

    #  ============================================================================================
    #
    #    (deep)copy support: methods prefix = _cp_
    #    cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#deepcopy-support
    #
    #  ============================================================================================

    def _cp_shall_create_copy_impl(self, copy_or_deepcopy: str) -> bool:
        if copy_or_deepcopy == "copy":
            match_regex = self.options.class_copy__regex
        else:
            match_regex = self.options.class_deep_copy__regex

        if not code_utils.does_match_regex(match_regex, self.cpp_element().class_name):
            return False

        user_defined_copy_constructor = self.cpp_element().get_user_defined_copy_constructor()
        if user_defined_copy_constructor is None:
            return True
        else:
            is_api = self.cpp_element().is_user_defined_copy_constructor_part_of_api()
            return is_api

    def _cp_shall_create_deep_copy(self) -> bool:
        return self._cp_shall_create_copy_impl("deep_copy")

    def _cp_shall_create_copy(self) -> bool:
        return self._cp_shall_create_copy_impl("copy")

    def _cp_stub_comment(self) -> str:
        if not self.options.class_copy_add_info_in_stub:
            return ""
        supported_list = []
        if self._cp_shall_create_copy():
            supported_list.append("copy.copy")
        if self._cp_shall_create_deep_copy():
            supported_list.append("copy.deepcopy")

        if len(supported_list) > 0:
            all_supported = " and ".join(supported_list)
            r = f"(has support for {all_supported})"
            return r
        else:
            return ""

    def _cp_pydef(self) -> str:
        code_template = code_utils.unindent_code(
            """
            .def("__{copy_or_deep_copy}__",  [](const {qualified_class_name} &self{maybe_pydict}) {
            {_i_}return {qualified_class_name}(self);
            }{maybe_memo})
        """,
            flag_strip_empty_lines=True,
        )

        replacements = munch.Munch()
        replacements._i_ = self.options._indent_cpp_spaces()
        replacements.qualified_class_name = self.cpp_element().qualified_class_name_with_specialization()

        full_code = ""
        for copy_or_deep_copy in ["copy", "deepcopy"]:
            replacements.copy_or_deep_copy = copy_or_deep_copy
            shall_create = self._cp_shall_create_copy_impl(copy_or_deep_copy)

            if copy_or_deep_copy == "copy":
                replacements.maybe_pydict = ""
                replacements.maybe_memo = ""
            else:
                py = "py" if self.options.bind_library == BindLibraryType.pybind11 else "nb"
                replacements.maybe_pydict = f", {py}::dict"
                replacements.maybe_memo = f', {py}::arg("memo")'

            if shall_create:
                code = code_utils.process_code_template(code_template, replacements)
                if len(full_code) > 0:
                    full_code += "\n"
                full_code += code

        return full_code

    #  ============================================================================================
    #
    #    Template classes support: methods prefix = _tpl_
    #    cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html?highlight=template#binding-classes-with-template-parameters
    #
    #  ============================================================================================

    def _tpl_is_one_param_template(self) -> bool:
        assert self.cpp_element().is_template_partially_specialized()
        nb_template_parameters = len(self.cpp_element().template.parameter_list.parameters)
        is_supported = nb_template_parameters == 1
        return is_supported

    def _tpl_instantiate_template_for_type(self, cpp_type: CppType) -> AdaptedClass:
        assert self.cpp_element().is_template_partially_specialized()
        assert self._tpl_is_one_param_template()

        new_cpp_class = self.cpp_element().with_specialized_template(CppTemplateSpecialization.from_type(cpp_type))
        assert new_cpp_class is not None
        new_adapted_class = AdaptedClass(self.lg_context, new_cpp_class)

        from litgen.internal import template_options

        tpl_class_name_python = cpp_to_python._class_name_to_python(self.options, self.cpp_element().class_name)
        instantiated_cpp_type_str = cpp_type.str_code()
        new_class_name_python = template_options._apply_template_naming(
            tpl_class_name_python, instantiated_cpp_type_str
        )
        new_class_name_python = cpp_to_python.type_to_python(self.lg_context, new_class_name_python)

        new_adapted_class.template_specialization = AdaptedClass.TemplateSpecialization(new_class_name_python, cpp_type)

        return new_adapted_class

    def _tpl_split_into_template_instantiations(self) -> _AdaptedInstantiatedTemplateClasses:
        assert self.cpp_element().is_template_partially_specialized()

        matching_template_spec = None
        for template_spec in self.options.class_template_options.specs:
            if code_utils.does_match_regex(template_spec.name_regex, self.cpp_element().class_name):
                matching_template_spec = template_spec

        if matching_template_spec is None:
            self.cpp_element().emit_warning(
                f"Ignoring template class {self.cpp_element().class_name} . You might need to set LitgenOptions.class_template_options",
                WarningType.LitgenTemplateClassIgnore,
            )
            return _AdaptedInstantiatedTemplateClasses([], [])

        if not self._tpl_is_one_param_template() and len(matching_template_spec.cpp_types_list) > 0:
            self.cpp_element().emit_warning(
                f"Template class {self.cpp_element().class_name} with more than one parameter is not supported",
                WarningType.LitgenTemplateClassMultipleIgnore,
            )
            return _AdaptedInstantiatedTemplateClasses([], [])

        new_classes: list[AdaptedClass] = []
        for cpp_type in matching_template_spec.cpp_types_list:
            new_class = self._tpl_instantiate_template_for_type(cpp_type)
            new_classes.append(new_class)

        stubs_synonym_code = []
        for cpp_synonym in matching_template_spec.cpp_types_synonyms:
            tpl_class_name_python = cpp_to_python._class_name_to_python(self.options, self.cpp_element().class_name)
            syn_python = cpp_to_python._class_name_to_python(self.options, cpp_synonym.synonym_name)
            target_python = cpp_to_python._class_name_to_python(self.options, cpp_synonym.synonym_target)
            tpl_syn_python = template_options._apply_template_naming(tpl_class_name_python, syn_python)
            tpl_target_python = template_options._apply_template_naming(tpl_class_name_python, target_python)
            stubs_synonym_code.append(f"{tpl_syn_python} = {tpl_target_python}")

        return _AdaptedInstantiatedTemplateClasses(new_classes, stubs_synonym_code)

    #  ============================================================================================
    #
    #    Overriding virtual functions in python: methods prefix = _virt_
    #    cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
    #    cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#combining-virtual-functions-and-inheritance
    #
    #  ============================================================================================

    def _virt_method_list_including_inherited(self) -> list[CppFunctionDecl]:
        r = self.cpp_element().virtual_methods(include_inherited_virtual_methods=True)
        return r

    def _virt_store_glue_override(self) -> None:
        """If needed, add glue code (a trampoline class) in order to be able to override methods from python.

        See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
        """
        if not self._virt_shall_override():
            return

        virtual_methods = self._virt_method_list_including_inherited()
        nb_virtual_methods = len(virtual_methods)

        if self.options.bind_library == litgen.BindLibraryType.pybind11:
            trampoline_class_template = code_utils.unindent_code(
                """
                // helper type to enable overriding virtual methods in python
                class {trampoline_class_name} : public {class_name}
                {
                public:
                    using {class_name}::{class_name};

                {trampoline_list}
                };
                """,
                flag_strip_empty_lines=True,
            )
        else:
            trampoline_class_template = code_utils.unindent_code(
                """
                // helper type to enable overriding virtual methods in python
                class {trampoline_class_name} : public {class_name}
                {
                public:
                    NB_TRAMPOLINE({class_name}, {nb_virtual_methods});

                {trampoline_list}
                };
                """,
                flag_strip_empty_lines=True,
            )

        trampoline_lines = []
        virtual_methods = self._virt_method_list_including_inherited()
        for virtual_method in virtual_methods:
            is_overloaded = False
            adapted_virtual_method = AdaptedFunction(self.lg_context, virtual_method, is_overloaded)
            qualified_class_name = self.cpp_element().cpp_scope_str(include_self=True)
            trampoline_lines += adapted_virtual_method.virt_glue_override_virtual_methods_in_python(
                qualified_class_name
            )

        replacements = munch.Munch()
        replacements.trampoline_class_name = self.cpp_element().class_name + "_trampoline"
        replacements.nb_virtual_methods = str(nb_virtual_methods)
        replacements.class_name = self.cpp_element().class_name
        replacements.trampoline_list = code_utils.indent_code(
            "\n".join(trampoline_lines), indent_str=self.options._indent_cpp_spaces()
        )

        publicist_class_code = code_utils.process_code_template(trampoline_class_template, replacements, {})

        ns_intro, ns_outro = self._glue_scope_intro_outro()

        glue_code: list[str] = []
        glue_code += [ns_intro]
        glue_code += publicist_class_code.split("\n")
        glue_code += [ns_outro]

        glue_code_str = "\n" + "\n".join(glue_code) + "\n"
        self.lg_context.virtual_methods_glue_code += glue_code_str

    def _virt_shall_override(self) -> bool:
        active = code_utils.does_match_regex(
            self.options.class_override_virtual_methods_in_python__regex, self.cpp_element().class_name
        )
        if not active:
            return False
        virtual_methods = self._virt_method_list_including_inherited()
        r = len(virtual_methods) > 0
        return r

    def _glue_scope_intro_outro(self) -> tuple[str, str]:
        scope = self.cpp_element().cpp_scope(False)
        nb_scope_parts = len(scope.scope_parts)
        intro = ""
        outro = "} " * nb_scope_parts

        for scope_part in scope.scope_parts:
            if scope_part.scope_type == CppScopeType.Namespace:
                intro += f"namespace {scope_part.scope_name} {{ "
            else:
                raise SrcmlcppException("Bad scope for protected member")

        for scope_part in reversed(scope.scope_parts):
            if scope_part.scope_type == CppScopeType.Namespace:
                outro += f" // namespace {scope_part.scope_name} "

        return intro, outro

    #  ============================================================================================
    #
    #    Publish protected methods: methods prefix = _prot_
    #    cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions
    #
    #  ============================================================================================

    def _prot_store_glue(self) -> None:
        """if needed, add glue code (a publicist class) to be able to publish protected methods.

        See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions
        """
        if not self._prot_shall_publish():
            return
        if len(self.adapted_protected_methods) == 0:
            return

        def using_list() -> list[str]:
            r = []
            for child in self.adapted_protected_methods:
                class_name = self.cpp_element().class_name
                method_name = child.cpp_element().function_name
                r.append(f"using {class_name}::{method_name};")
            return r

        publicist_class_template = code_utils.unindent_code(
            """
            // helper type for exposing protected functions
            class {publicist_class_name} : public {class_name}
            {
            public:
            {using_list}
            };
        """,
            flag_strip_empty_lines=True,
        )

        replacements = munch.Munch()
        replacements.publicist_class_name = self.cpp_element().class_name + "_publicist"
        replacements.class_name = self.cpp_element().class_name
        replacements.using_list = code_utils.indent_code(
            "\n".join(using_list()), indent_str=self.options._indent_cpp_spaces()
        )

        publicist_class_code = code_utils.process_code_template(publicist_class_template, replacements, {})

        ns_intro, ns_outro = self._glue_scope_intro_outro()

        glue_code: list[str] = []
        glue_code += [ns_intro]
        glue_code += publicist_class_code.split("\n")
        glue_code += [ns_outro]

        glue_code_str = "\n" + "\n".join(glue_code) + "\n"
        self.lg_context.protected_methods_glue_code += glue_code_str

    def _prot_fill_methods(self) -> None:
        if not self._prot_shall_publish():
            return
        for child in self.cpp_element().get_elements(access_type=CppAccessType.protected):
            if isinstance(child, CppFunctionDecl):
                if AdaptedFunction.init_is_function_publishable(self.options, child):
                    is_overloaded = child.is_overloaded_method()
                    self.adapted_protected_methods.append(AdaptedFunction(self.lg_context, child, is_overloaded))

    def _prot_shall_publish(self) -> bool:
        r = code_utils.does_match_regex(
            self.options.class_expose_protected_methods__regex, self.cpp_element().class_name
        )
        return r


class PythonNamedConstructorHelper:
    adapted_class: AdaptedClass
    cpp_class: CppStruct
    options: litgen.LitgenOptions

    def __init__(self, adapted_class: AdaptedClass) -> None:
        self.adapted_class = adapted_class
        self.cpp_class = adapted_class.cpp_element()
        self.options = self.adapted_class.options
        assert (
            not self.cpp_class.has_deleted_default_constructor() and not self.cpp_class.has_user_defined_constructor()
        )

    def flag_generate_named_ctor_params(self) -> bool:
        cpp_class = self.adapted_class.cpp_element()
        ctor__regex = ""
        if type(cpp_class) is CppClass:
            ctor__regex = self.options.class_create_default_named_ctor__regex
        elif type(cpp_class) is CppStruct:
            ctor__regex = self.options.struct_create_default_named_ctor__regex
        result = code_utils.does_match_regex(ctor__regex, self.adapted_class.cpp_element().class_name)

        if cpp_class.has_private_destructor():
            result = False
        if cpp_class.has_user_defined_default_constructor_non_zero_param():
            # There is already a specialized constructor with some params => bail out!
            result = False
        return result

    def flag_generate_void_constructor(self) -> bool:
        result = (
            not self.adapted_class.cpp_element().has_user_defined_constructor()
            and not self.flag_generate_named_ctor_params()
        )
        return result

    def named_constructor_decl(self) -> CppFunctionDecl:
        options = self.adapted_class.options

        def compatible_members_list() -> list[CppDecl]:
            """The list of members which we will include in the named params"""
            if not self.flag_generate_named_ctor_params():
                return []

            members_decls = self.cpp_class.get_members(access_type=CppAccessType.public)

            def not_excluded_tpl(member: CppDecl) -> bool:
                return not options.class_template_options.shall_exclude_type(member.cpp_type)

            members_decls = list(filter(not_excluded_tpl, members_decls))

            def can_be_set(member: CppDecl) -> bool:
                if member.cpp_type.modifiers.count("*") > 1:
                    return False  # refuse double pointers

                specifiers = member.cpp_type.specifiers
                if "const" in specifiers or "constexpr" in specifiers or "extern" in specifiers:
                    return False

                if len(member.bitfield_range) > 0:
                    return False  # Refuse bitfields!

                if len(member.c_array_code) > 0:
                    return False  # Refuse c style arrays

                if member.cpp_type.modifiers.count("*") > 0:
                    return False  # refuse pointers

                if member.cpp_type.modifiers.count("&") > 0:
                    return False  # refuse references

                cpp_type_str = member.cpp_type.str_code()
                if " " in cpp_type_str:
                    # refuse types with spaces like "unsigned int"
                    # they introduce too many syntax exceptions
                    return False

                if code_utils.does_match_regex(options.member_exclude_by_type__regex, cpp_type_str):
                    return False

                if code_utils.does_match_regex(options.member_exclude_by_name__regex, member.name()):
                    return False

                cls_name = self.cpp_class.class_name
                regex_str = options.member_exclude_by_name_and_class__regex.get(cls_name, "")
                if code_utils.does_match_regex(regex_str, member.name()):
                    return False

                return True

            members_decls = list(filter(can_be_set, members_decls))
            return members_decls

        def make_fake_struct_cpp_code() -> str:
            class_name = self.adapted_class.cpp_element().class_name
            members = compatible_members_list()
            members_strs = []
            for member in members:
                s = f"{member.cpp_type.str_code()} {member.name()}"
                if len(member.initial_value_code) > 0:
                    s += " = " + member.initial_value_code
                else:
                    cpp_type_str = member.cpp_type.str_code()
                    s += " = " + cpp_type_str + "()"
                members_strs.append(s)
            parameters_str = ", ".join(members_strs)
            str_cpp_code = f"""
                struct {class_name} {{
                    {class_name}({parameters_str});
                }};
            """

            class_scope = self.adapted_class.cpp_element().cpp_scope()
            for scope_part in class_scope.scope_parts:
                if scope_part.scope_type == CppScopeType.Namespace:
                    str_cpp_code = "namespace " + scope_part.scope_name + "{\n" + str_cpp_code + "\n" + "}\n"
                if scope_part.scope_type == CppScopeType.ClassOrStruct:
                    # We reinterpret the struct as a namespace, this does not change the scope
                    str_cpp_code = "namespace " + scope_part.scope_name + "{\n" + str_cpp_code + "\n" + "}\n"

            return str_cpp_code

        def make_cpp_constructor() -> CppFunctionDecl:
            def make_cpp_unit_quiet(options: litgen.LitgenOptions, code: str) -> CppUnit:
                flag_progress = options.srcmlcpp_options.flag_show_progress
                options.srcmlcpp_options.flag_show_progress = False
                unit = srcmlcpp.code_to_cpp_unit(options.srcmlcpp_options, code)
                options.srcmlcpp_options.flag_show_progress = flag_progress
                return unit

            cpp_code = make_fake_struct_cpp_code()
            cpp_unit = make_cpp_unit_quiet(self.adapted_class.options, cpp_code)

            # We have a CppUnit, that represents a struct, but we need to reparent the constructor
            #      srcmlcpp xml "struct Foo { Foo(); };"
            #        <struct>struct
            #           <name>Foo</name>
            #           <block>{
            #              <public type="default">    <=======   reattach this public to the block of the correct class
            #                 <constructor_decl> <name>Foo</name>
            #                    <parameter_list>()</parameter_list>;
            #                 </constructor_decl>
            #              </public>}
            #           </block>;
            #        </struct>
            public_regions = cpp_unit.all_cpp_elements_recursive(CppPublicProtectedPrivate)
            assert len(public_regions) == 1
            public_region = public_regions[0]
            public_region.parent = self.adapted_class.cpp_element().block

            # Find the constructor
            ctors = cpp_unit.all_cpp_elements_recursive(CppConstructorDecl)
            assert len(ctors) == 1
            ctor_decl = cast(CppConstructorDecl, ctors[0])
            if self.flag_generate_void_constructor():
                ctor_decl.cpp_element_comments.comment_on_previous_lines = (
                    "Auto-generated default constructor (omit named params)"
                )
            else:
                if len(ctor_decl.parameter_list.parameters) > 0:
                    ctor_decl.cpp_element_comments.comment_on_previous_lines = (
                        "Auto-generated default constructor with named params"
                    )
                else:
                    ctor_decl.cpp_element_comments.comment_on_previous_lines = "Auto-generated default constructor"
            # And qualify its types
            ctor_qualified = ctor_decl.with_qualified_types()
            return ctor_qualified

        return make_cpp_constructor()

    def pydef_code(self) -> str:
        _i_ = self.adapted_class.options._indent_cpp_spaces()
        if self.flag_generate_void_constructor():
            py = "py" if self.options.bind_library == BindLibraryType.pybind11 else "nb"
            return f"{_i_}.def({py}::init<>()) // implicit default constructor\n"
        if not self.flag_generate_named_ctor_params():
            return ""
        ctor_decl = self.named_constructor_decl()

        if (
            len(ctor_decl.parameter_list.parameters) == 0
            and self.cpp_class.has_user_defined_default_constructor_zero_param()
        ):
            return ""

        lg_context = self.adapted_class.lg_context
        adapted_ctor = AdaptedFunction(lg_context, ctor_decl, False)
        # We modify ctor_decl, because adapt_mutable_param_with_default_value may change it
        # (we keep a backup of the original, to be able to compare)
        ctor_decl_adapted = adapted_ctor.cpp_adapted_function


        if len(ctor_decl.parameter_list.parameters) == 0:
            py = "py" if self.options.bind_library == BindLibraryType.pybind11 else "nb"
            return f"{_i_}.def({py}::init<>()) // implicit default constructor \n"

        if self.options.bind_library == BindLibraryType.pybind11:
            template = code_utils.unindent_code(
                """
                .def(py::init<>([](
                {all_params_signature})
                {
                {_i_}auto r = std::make_unique<{qualified_struct_name}>();
                {all_params_set_values}
                {_i_}return r;
                })
                , {maybe_pyargs}
                )
            """,
                flag_strip_empty_lines=True,
            )
        else:
            template = code_utils.unindent_code(
                """
                .def("__init__", []({all_params_signature})
                {
                {_i_}new (self) {qualified_struct_name}();  // placement new
                {_i_}auto r = self;
                {all_params_set_values}
                },
                {maybe_pyargs}
                )
            """,
                flag_strip_empty_lines=True,
            )

        replacements = munch.Munch()
        replacements._i_ = _i_
        replacements.qualified_struct_name = self.cpp_class.qualified_class_name_with_specialization()
        replacements.all_params_signature = ctor_decl_adapted.parameter_list.str_types_names_default_for_signature()

        replacements_lines = munch.Munch()
        replacements_lines.maybe_pyargs = ", ".join(adapted_ctor._pydef_pyarg_list())

        def get_all_params_set_values() -> str:
            from litgen.internal.adapt_function_params._adapt_mutable_param_with_default_value import was_mutable_param_with_default_value_made_optional
            original_parameters = ctor_decl.parameter_list.parameters
            modified_parameters = ctor_decl_adapted.parameter_list.parameters
            # Remove first "self" parameter from modified_parameters (may have been added by AdaptedFunction, if using nanobind)
            if len(modified_parameters) > 0 and modified_parameters[0].decl.name() == "self":
                modified_parameters = modified_parameters[1:]
            assert len(original_parameters) == len(modified_parameters)

            all_params_set_values_list = []
            for i in range(len(modified_parameters)):
                original_param = original_parameters[i]
                modified_param = modified_parameters[i]
                if was_mutable_param_with_default_value_made_optional(lg_context, original_param):
                    code = f"""
                    if ({modified_param.decl.name()}.has_value())
                    {_i_}r->{modified_param.decl.name()} = {modified_param.decl.name()}.value();
                    else
                    {_i_}r->{modified_param.decl.name()} = {original_param.decl.initial_value_code};
                    """
                    code = code_utils.unindent_code(code, flag_strip_empty_lines=True)

                else:
                    code = f"r->{original_param.decl.name()} = {original_param.decl.name()};"
                all_params_set_values_list.append(code)
            all_params_set_values = "\n".join(all_params_set_values_list)
            all_params_set_values = code_utils.indent_code(all_params_set_values, indent_str=_i_)
            return all_params_set_values

        replacements.all_params_set_values = get_all_params_set_values()

        final_code = code_utils.process_code_template(template, replacements, replacements_lines)
        final_code = code_utils.indent_code(final_code, indent_str=_i_) + "\n"

        return final_code

    def stub_code(self) -> str:
        if self.flag_generate_void_constructor():
            r = code_utils.unindent_code(
                '''
            def __init__(self) -> None:
                """Autogenerated default constructor"""
                pass
            ''',
                flag_strip_empty_lines=True,
            )
            return r
        if not self.flag_generate_named_ctor_params():
            return ""
        ctor_decl = self.named_constructor_decl()
        if (
            len(ctor_decl.parameter_list.parameters) == 0
            and self.cpp_class.has_user_defined_default_constructor_zero_param()
        ):
            return ""

        adapted_function = AdaptedFunction(self.adapted_class.lg_context, ctor_decl, False)

        r = "\n".join(adapted_function.stub_lines())
        return r

    def __repr__(self):
        return f"PythonNamedConstructorHelper({self.adapted_class})"
