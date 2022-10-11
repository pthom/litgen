from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union, cast

import munch  # type: ignore

from codemanip import code_utils

from srcmlcpp.cpp_types import *
from srcmlcpp.cpp_types.cpp_scope import CppScopeType
from srcmlcpp.srcmlcpp_exception import SrcmlcppException

from litgen import TemplateNamingScheme
from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_enum import AdaptedEnum
from litgen.internal.adapted_types.adapted_function import AdaptedFunction
from litgen.internal.context.litgen_context import LitgenContext


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
        if array_typename not in options.member_numeric_c_array_types_list():
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
        if array_typename not in options.member_numeric_c_array_types_list():
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Only numeric C Style arrays are supported
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
            )
            return False

        shall_replace = code_utils.does_match_regex(options.member_numeric_c_array_replace__regex, cpp_decl.decl_name)
        if not shall_replace:
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Detected a numeric C Style array, but will not export it.
                Hint: modify `options.member_numeric_c_array_replace__regex`
                """,
            )
            return False

        if cpp_decl.c_array_size_as_int() is None:
            array_size_str = cpp_decl.c_array_size_as_str()
            cpp_decl.emit_warning(
                f"""
                AdaptedClassMember: Detected a numeric C Style array, but its size is not parsable.
                Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                """,
            )
            return False

        return True

    def check_can_publish(self) -> bool:
        """Returns true if this member can be published as a property of the class"""
        cpp_decl = self.cpp_element()

        if cpp_decl.is_bitfield():  # is_bitfield()
            cpp_decl.emit_warning(
                f"AdaptedClassMember: Skipped bitfield member {cpp_decl.decl_name}",
            )
            return False
        elif cpp_decl.is_c_array_fixed_size_unparsable():
            cpp_decl.emit_warning(
                """
                AdaptedClassMember: Can't parse the size of this array.
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
            )
            return False
        elif cpp_decl.is_c_array_known_fixed_size():
            return self._check_can_add_c_array_known_fixed_size()
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

    def _str_pydef_lines_numeric_array(self) -> List[str]:
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11

        qualified_struct_name = self.class_parent.cpp_element().qualified_class_name_with_specialization()
        location = self.info_original_location_cpp()
        name_python = self.decl_name_python()
        name_cpp = self.decl_name_cpp()
        comment = self.comment_pydef_one_line()

        array_typename = self.cpp_element().cpp_type.str_code()
        array_size = self.cpp_element().c_array_size_as_int()
        assert array_size is not None

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
        r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True)  # + "\n"
        lines = r.split("\n")
        return lines

    def _str_pydef_lines_field(self) -> List[str]:
        qualified_struct_name = self.class_parent.cpp_element().qualified_class_name_with_specialization()
        location = self.info_original_location_cpp()
        name_python = self.decl_name_python()
        name_cpp = self.decl_name_cpp()
        comment = self.comment_pydef_one_line()

        pybind_definition_mode = "def_readwrite"
        cpp_type = self.cpp_element().cpp_type
        if cpp_type.is_const():
            pybind_definition_mode = "def_readonly"
        if cpp_type.is_static():
            pybind_definition_mode += "_static"

        r = f'.{pybind_definition_mode}("{name_python}", &{qualified_struct_name}::{name_cpp}, "{comment}"){location}'
        return [r]

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        code_lines: List[str] = []

        if not self.comment_python_shall_place_at_end_of_line():
            code_lines += self.comment_python_previous_lines()

        decl_name_python = self.decl_name_python()
        decl_type_python = self.decl_type_python()

        default_value_python = self.decl_value_python()
        if len(default_value_python) > 0:
            maybe_defaultvalue_python = default_value_python
            maybe_equal = " = "
        else:
            maybe_defaultvalue_python = ""
            maybe_equal = ""

        if not self.comment_python_shall_place_at_end_of_line():
            maybe_comment = ""
        else:
            maybe_comment = self.comment_python_end_of_line()

        maybe_comment_array = self.comment_array()

        location = self.info_original_location_python()

        maybe_static_info = " # (C++ static member)" if self.cpp_element().cpp_type.is_static() else ""

        decl_template = f"{decl_name_python}: {decl_type_python}{maybe_equal}{maybe_defaultvalue_python}{maybe_comment_array}{maybe_comment}{maybe_static_info}{location}"
        code_lines += [decl_template]

        code_lines = self._cpp_original_code_lines() + code_lines
        return code_lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        if self._is_numeric_c_array():
            return self._str_pydef_lines_numeric_array()
        else:
            return self._str_pydef_lines_field()


@dataclass
class AdaptedClass(AdaptedElement):
    adapted_public_children: List[
        Union[AdaptedEmptyLine, AdaptedComment, AdaptedClassMember, AdaptedFunction, AdaptedClass, AdaptedEnum]
    ]
    adapted_protected_methods: List[AdaptedFunction]

    @dataclass
    class TemplateSpecialization:
        class_name_python: str = ""
        cpp_type: str = ""

    template_specialization: Optional[TemplateSpecialization] = None

    def __init__(self, lg_context: LitgenContext, class_: CppStruct):
        super().__init__(lg_context, class_)
        self.adapted_public_children = []
        self._fill_public_children()

        self.adapted_protected_methods = []
        self._fill_protected_methods()

    def __str__(self):
        r = f"AdaptedClass({self.cpp_element().class_name})"
        return r

    # override
    def cpp_element(self) -> CppStruct:
        return cast(CppStruct, self._cpp_element)

    def class_name_python(self) -> str:
        if self.template_specialization is not None:
            return self.template_specialization.class_name_python
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().class_name)
        return r

    def _shall_publish_protected_methods(self) -> bool:
        r = code_utils.does_match_regex(
            self.options.class_expose_protected_methods__regex, self.cpp_element().class_name
        )
        return r

    def _shall_override_virtual_methods_in_python(self) -> bool:
        active = code_utils.does_match_regex(
            self.options.class_override_virtual_methods_in_python__regex, self.cpp_element().class_name
        )
        if not active:
            return False
        virtual_methods = self._virtual_method_list_including_inherited()
        r = len(virtual_methods) > 0
        return r

    def _add_adapted_class_member(self, cpp_decl_statement: CppDeclStatement) -> None:
        for cpp_decl in cpp_decl_statement.cpp_decls:
            is_excluded_by_name = code_utils.does_match_regex(
                self.options.member_exclude_by_name__regex, cpp_decl.decl_name
            )
            is_excluded_by_type = code_utils.does_match_regex(
                self.options.member_exclude_by_type__regex, cpp_decl.cpp_type.str_code()
            )
            if not is_excluded_by_name and not is_excluded_by_type:
                adapted_class_member = AdaptedClassMember(self.lg_context, cpp_decl, self)
                if adapted_class_member.check_can_publish():
                    self.adapted_public_children.append(adapted_class_member)

    def _fill_protected_methods(self) -> None:
        if not self._shall_publish_protected_methods():
            return
        for child in self.cpp_element().get_elements(access_type=CppAccessTypes.protected):
            if isinstance(child, CppFunctionDecl):
                if AdaptedFunction.is_function_publishable(self.options, child):
                    is_overloaded = child.is_overloaded_method()
                    self.adapted_protected_methods.append(AdaptedFunction(self.lg_context, child, is_overloaded))

    def _fill_public_children(self) -> None:
        public_elements = self.cpp_element().get_elements(access_type=CppAccessTypes.public)
        for child in public_elements:
            try:
                if isinstance(child, CppEmptyLine):
                    self.adapted_public_children.append(AdaptedEmptyLine(self.lg_context, child))
                elif isinstance(child, CppComment):
                    self.adapted_public_children.append(AdaptedComment(self.lg_context, child))
                elif isinstance(child, CppFunctionDecl):
                    if AdaptedFunction.is_function_publishable(self.options, child):
                        is_overloaded = child.is_overloaded_method()
                        self.adapted_public_children.append(AdaptedFunction(self.lg_context, child, is_overloaded))
                elif isinstance(child, CppDeclStatement):
                    self._add_adapted_class_member(child)
                elif isinstance(child, CppUnprocessed):
                    continue
                elif isinstance(child, CppStruct):
                    adapted_subclass = AdaptedClass(self.lg_context, child)
                    self.adapted_public_children.append(adapted_subclass)
                elif isinstance(child, CppEnum):
                    adapted_enum = AdaptedEnum(self.lg_context, child)
                    self.adapted_public_children.append(adapted_enum)
                else:
                    child.emit_warning(
                        f"Public elements of type {child.tag()} are not supported in python conversion",
                    )
            except SrcmlcppException as e:
                child.emit_warning(str(e))

    def _str_parent_classes(self) -> str:
        parents: List[str] = []
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

    # override
    def _str_stub_lines(self) -> List[str]:
        # If this is a template class, implement as many versions
        # as mentioned in the options (see LitgenOptions.class_template_options)
        # and bail out
        if self.cpp_element().is_template_partially_specialized():
            template_instantiations = self._split_into_template_instantiations()
            if len(template_instantiations) == 0:
                self.cpp_element().emit_warning(
                    "Ignoring template class. You might need to set LitgenOptions.class_template_options"
                )
                return []
            else:
                r: List[str] = []
                for template_instantiation in template_instantiations:
                    if len(r) > 0:
                        r += ["", ""]  # 2 empty lines between classes
                    r += template_instantiation._str_stub_lines()
                if self.options.class_template_decorate_in_stub:
                    r = cpp_to_python.surround_python_code_lines(
                        r, f"template specializations for class {self.cpp_element().class_name}"
                    )
                return r

        from litgen.internal.adapted_types.line_spacer import LineSpacerPython

        line_spacer = LineSpacerPython(self.options)

        class_name = self.class_name_python()

        title = f"class {class_name}{self._str_parent_classes()}:"
        title_lines = [title]
        if self.cpp_element().is_final():
            self.cpp_element().cpp_element_comments.comment_on_previous_lines += "\n"
            self.cpp_element().cpp_element_comments.comment_on_previous_lines += "(final class)"

        body_lines: List[str] = []
        for element in self.adapted_public_children:
            element_lines = element._str_stub_lines()

            spacing_lines = line_spacer.spacing_lines(element, element_lines)
            body_lines += spacing_lines
            body_lines += element_lines

        if len(self.adapted_protected_methods) > 0:
            body_lines += ["", "# <protected_methods>"]
            for element in self.adapted_protected_methods:
                element_lines = element._str_stub_lines()

                spacing_lines = line_spacer.spacing_lines(element, element_lines)
                body_lines += spacing_lines
                body_lines += element_lines
            body_lines += ["# </protected_methods>", ""]

        r = self._str_stub_layout_lines(title_lines, body_lines)
        return r

    def _scope_intro_outro(self) -> Tuple[str, str]:
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

    def _virtual_method_list_including_inherited(self) -> List[CppFunctionDecl]:
        r = self.cpp_element().virtual_methods(include_inherited_virtual_methods=True)
        return r

    def _store_glue_override_virtual_methods_in_python(self) -> None:
        # See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
        if not self._shall_override_virtual_methods_in_python():
            return

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

        trampoline_lines = []
        virtual_methods = self._virtual_method_list_including_inherited()
        for virtual_method in virtual_methods:
            is_overloaded = False
            adapted_virtual_method = AdaptedFunction(self.lg_context, virtual_method, is_overloaded)
            qualified_class_name = self.cpp_element().cpp_scope(include_self=True).str_cpp()
            trampoline_lines += adapted_virtual_method.glue_override_virtual_methods_in_python(qualified_class_name)

        replacements = munch.Munch()
        replacements.trampoline_class_name = self.cpp_element().class_name + "_trampoline"
        replacements.class_name = self.cpp_element().class_name
        replacements.trampoline_list = code_utils.indent_code(
            "\n".join(trampoline_lines), indent_str=self.options.indent_cpp_spaces()
        )

        publicist_class_code = code_utils.process_code_template(trampoline_class_template, replacements, {})

        ns_intro, ns_outro = self._scope_intro_outro()

        glue_code: List[str] = []
        glue_code += [ns_intro]
        glue_code += publicist_class_code.split("\n")
        glue_code += [ns_outro]

        glue_code_str = "\n" + "\n".join(glue_code) + "\n"
        self.lg_context.virtual_methods_glue_code += glue_code_str

    def _store_glue_protected_methods(self) -> None:
        # See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions
        if not self._shall_publish_protected_methods():
            return
        if len(self.adapted_protected_methods) == 0:
            return

        def using_list() -> List[str]:
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
            "\n".join(using_list()), indent_str=self.options.indent_cpp_spaces()
        )

        publicist_class_code = code_utils.process_code_template(publicist_class_template, replacements, {})

        ns_intro, ns_outro = self._scope_intro_outro()

        glue_code: List[str] = []
        glue_code += [ns_intro]
        glue_code += publicist_class_code.split("\n")
        glue_code += [ns_outro]

        glue_code_str = "\n" + "\n".join(glue_code) + "\n"
        self.lg_context.protected_methods_glue_code += glue_code_str

    def _is_one_param_template(self) -> bool:
        assert self.cpp_element().is_template_partially_specialized()
        nb_template_parameters = len(self.cpp_element().template.parameter_list.parameters)
        is_supported = nb_template_parameters == 1
        return is_supported

    def _instantiate_template_for_type(self, cpp_type_str: str, naming_scheme: TemplateNamingScheme) -> AdaptedClass:
        assert self.cpp_element().is_template_partially_specialized()
        assert self._is_one_param_template()

        new_cpp_class = self.cpp_element().with_specialized_template(
            CppTemplateSpecialization.from_type_str(cpp_type_str)
        )
        assert new_cpp_class is not None
        new_adapted_class = AdaptedClass(self.lg_context, new_cpp_class)
        new_adapted_class.template_specialization = AdaptedClass.TemplateSpecialization(
            TemplateNamingScheme.apply(naming_scheme, self.cpp_element().class_name, cpp_type_str), cpp_type_str
        )

        return new_adapted_class

    def _split_into_template_instantiations(self) -> List[AdaptedClass]:
        assert self.cpp_element().is_template_partially_specialized()
        if not self._is_one_param_template():
            self.cpp_element().emit_warning("Only one parameter template classes are supported")
            return []

        for instantiation_spec in self.options.class_template_options.specs:
            if code_utils.does_match_regex(instantiation_spec.name_regex, self.cpp_element().class_name):
                new_classes: List[AdaptedClass] = []
                for cpp_type in instantiation_spec.cpp_types_list:
                    new_class = self._instantiate_template_for_type(cpp_type, instantiation_spec.naming_scheme)
                    new_classes.append(new_class)
                return new_classes
        return []

    # override
    def _str_pydef_lines(self) -> List[str]:
        # If this is a template class, implement as many versions
        # as mentioned in the options (see LitgenOptions.class_template_options)
        # and bail out
        if self.cpp_element().is_template_partially_specialized():
            template_instantiations = self._split_into_template_instantiations()
            if len(template_instantiations) == 0:
                self.cpp_element().emit_warning(
                    "Ignoring template class. You might need to set LitgenOptions.class_template_options"
                )
                return []
            else:
                r = []
                for template_instantiation in template_instantiations:
                    r += template_instantiation._str_pydef_lines()
                return r

        self._store_glue_protected_methods()
        self._store_glue_override_virtual_methods_in_python()

        options = self.options
        _i_ = options.indent_cpp_spaces()

        def make_pyclass_creation_code() -> str:
            qualified_struct_name = self.cpp_element().qualified_class_name_with_specialization()

            # fill py::class_ additional template params (base classes, nodelete, etc)
            other_template_params_list = []
            if self.cpp_element().has_base_classes():
                base_classes = self.cpp_element().base_classes()
                for access_type, base_class in base_classes:
                    if access_type == CppAccessTypes.public or access_type == CppAccessTypes.protected:
                        other_template_params_list.append(base_class.cpp_scope(include_self=True).str_cpp())
            if self.cpp_element().has_private_destructor():
                other_template_params_list.append(f"std::unique_ptr<{qualified_struct_name}, py::nodelete>")
            if self._shall_override_virtual_methods_in_python():
                scope = self.cpp_element().cpp_scope(False).str_cpp()
                scope_prefix = scope + "::" if len(scope) > 0 else ""
                qualified_trampoline_name = scope_prefix + self.cpp_element().class_name + "_trampoline"
                other_template_params_list.append(qualified_trampoline_name)

            if len(other_template_params_list) > 0:
                other_template_params = ", " + ", ".join(other_template_params_list)
            else:
                other_template_params = ""

            code_template = (
                code_utils.unindent_code(
                    """
                auto {pydef_class_var} =
                {_i_}py::class_<{qualified_struct_name}{other_template_params}>{location}
                {_i_}{_i_}({pydef_class_var_parent}, "{class_name_python}"{maybe_py_is_final}{maybe_py_is_dynamic}, "{comment}")
                """,
                    flag_strip_empty_lines=True,
                )
                + "\n"
            )

            replacements = munch.Munch()
            replacements._i_ = self.options.indent_cpp_spaces()
            replacements.pydef_class_var = cpp_to_python.cpp_scope_to_pybind_var_name(options, self.cpp_element())
            replacements.qualified_struct_name = qualified_struct_name
            replacements.other_template_params = other_template_params
            replacements.location = self.info_original_location_cpp()
            replacements.class_name_python = self.class_name_python()
            replacements.pydef_class_var_parent = cpp_to_python.cpp_scope_to_pybind_parent_var_name(
                options, self.cpp_element()
            )
            replacements.maybe_py_is_final = ", py::is_final()" if self.cpp_element().is_final() else ""
            if code_utils.does_match_regex(self.options.class_dynamic_attributes__regex, self.cpp_element().class_name):
                replacements.maybe_py_is_dynamic = ", py::dynamic_attr()"
            else:
                replacements.maybe_py_is_dynamic = ""

            replacements.comment = self.comment_pydef_one_line()

            pyclass_creation_code = code_utils.process_code_template(code_template, replacements)

            return pyclass_creation_code

        qualified_struct_name = self.cpp_element().qualified_class_name_with_specialization()
        if options.generate_to_string:
            code_outro = f'{_i_}.def("__repr__", [](const {qualified_struct_name}& v) {{ return ToString(v); }});'
        else:
            code_outro = f"{_i_};"

        code = make_pyclass_creation_code()

        if (
            not self.cpp_element().has_user_defined_constructor()
            and not self.cpp_element().has_deleted_default_constructor()
        ):
            code += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
        if self.cpp_element().has_deleted_default_constructor():
            code += f"{_i_}// (default constructor explicitly deleted)\n"

        def is_class_or_enum(e: AdaptedElement) -> bool:
            return isinstance(e, AdaptedClass) or isinstance(e, AdaptedEnum)

        def not_is_class_or_enum(e: AdaptedElement) -> bool:
            return not (isinstance(e, AdaptedClass) or isinstance(e, AdaptedEnum))

        children_except_inner_classes = list(filter(not_is_class_or_enum, self.adapted_public_children))
        children_inner_classes = list(filter(is_class_or_enum, self.adapted_public_children))

        for child in children_except_inner_classes:
            decl_code = child.str_pydef()
            code += code_utils.indent_code(decl_code, indent_str=options.indent_cpp_spaces())

        for child in self.adapted_protected_methods:
            # Temporarily change the name of the parent struct, to use the publicist class
            parent_struct = child.cpp_element().parent_struct_if_method()
            assert parent_struct is not None
            original_class_name = parent_struct.class_name
            parent_struct.class_name = self.cpp_element().class_name + "_publicist"
            decl_code = child.str_pydef()
            parent_struct.class_name = original_class_name

            code += code_utils.indent_code(decl_code, indent_str=options.indent_cpp_spaces())

        code = code + code_outro

        if len(children_inner_classes) > 0:
            code += "\n{" + f" // inner classes & enums of {self.class_name_python()}\n"
            for child in children_inner_classes:
                decl_code = child.str_pydef()
                code += code_utils.indent_code(decl_code, indent_str=options.indent_cpp_spaces())
            code += "}" + f" // end of inner classes & enums of {self.class_name_python()}"

        lines = code.split("\n")
        return lines
