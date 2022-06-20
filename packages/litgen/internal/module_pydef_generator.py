import copy
import logging
import os
import sys
from typing import Union, cast

import srcmlcpp
from codemanip import code_replacements, code_utils
from litgen.internal import cpp_to_python
from litgen.internal.adapted_types_wip.adapted_types import AdaptedFunction
from litgen.internal.cpp_to_python import info_original_location_cpp
from litgen.internal.adapted_types_wip.adapted_types import *
from litgen.options import LitgenOptions
from srcmlcpp import srcml_main, srcml_warnings
from srcmlcpp.srcml_types import *


class _LineSpacer:
    last_element: Optional[CppElementAndComment] = None

    def line_spaces(self, element: CppElementAndComment):
        if self.last_element is None:
            self.last_element = element
            return ""

        standout_types = [CppEnum, CppStruct, CppNamespace]

        type_last = type(self.last_element)
        type_current = type(element)

        last_is_standout = type_last in standout_types
        current_is_standout = type_current in standout_types

        large_spacing = last_is_standout or current_is_standout
        r = "\n\n" if large_spacing else "\n"

        self.last_element = element

        return r


#################################
#           Enums
################################


def _generate_enum(enum: CppEnum, options: LitgenOptions) -> str:
    adapted_enum = AdaptedEnum(enum, options)
    r = adapted_enum.str_pydef()
    return r


#################################
#           Functions
################################


def _generate_function(
    function_infos: CppFunctionDecl,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> str:
    adapted_function = AdaptedFunction(function_infos, parent_struct_name, options)

    r = ""
    r += _generate_function_impl(adapted_function, options, parent_struct_name)
    return r


def _generate_function_impl(
    adapted_function: AdaptedFunction,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> str:
    r = adapted_function.str_pydef()
    return r


#################################
#           Methods
################################


def _generate_constructor(function_infos: CppConstructorDecl, options: LitgenOptions, parent_struct_name: str) -> str:
    adapted_function = AdaptedFunction(function_infos, parent_struct_name, options)
    r = adapted_function.str_pydef()
    return r


def _generate_method(function_infos: CppFunctionDecl, options: LitgenOptions, parent_struct_name: str) -> str:
    return _generate_function(function_infos, options, parent_struct_name)


#################################
#           Structs and classes
################################


def _add_struct_member_decl(cpp_decl: CppDecl, struct_name: str, options: LitgenOptions) -> str:
    _i_ = options.indent_cpp_spaces()
    name_cpp = cpp_decl.decl_name
    name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    comment = cpp_decl.cpp_element_comments.full_comment()
    location = info_original_location_cpp(cpp_decl, options)

    if len(cpp_decl.bitfield_range) > 0:
        # We ignore bitfields
        return ""

    if cpp_decl.is_c_array_fixed_size_unparsable(options.srcml_options):
        srcml_warnings.emit_srcml_warning(
            cpp_decl.srcml_element,
            """
            Can't parse the size of this array.
            Hint: use a vector, or extend `options.c_array_numeric_member_types`
            """,
            options.srcml_options,
        )
        return ""

    elif cpp_decl.is_c_array_known_fixed_size(options.srcml_options):
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options.c_array_numeric_member_types:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Only numeric C Style arrays are supported
                Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                options.srcml_options,
            )
            return ""

        if not options.c_array_numeric_member_flag_replace:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Detected a numeric C Style array, but will not export it.
                Hint: set `options.c_array_numeric_member_flag_replace = True`
                """,
                options.srcml_options,
            )
            return ""

        array_size = cpp_decl.c_array_size_as_int(options.srcml_options)

        if array_size is None:
            array_size_str = cpp_decl.c_array_size_as_str()
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                f"""
                Detected a numeric C Style array, but will not export it because its size is not parsable.
                Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                """,
                options.srcml_options,
            )
            return ""

        template_code = f"""
            .def_property("{name_python}",
                []({struct_name} &self) -> pybind11::array
                {{
                    auto dtype = pybind11::dtype(pybind11::format_descriptor<{array_typename}>::format());
                    auto base = pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}});
                    return pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}}, self.{name_cpp}, base);
                }}, []({struct_name}& self) {{}})
        """

        r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True) + "\n"
        return r

    else:
        code_inner_member = (
            f'.def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT"){location}\n'
        )
        r = code_inner_member
        r = r.replace("MEMBER_NAME_PYTHON", name_python)
        r = r.replace("MEMBER_NAME_CPP", name_cpp)
        r = r.replace("MEMBER_COMMENT", cpp_to_python.comment_pydef_one_line(comment, options))
        return r


def _add_struct_member_decl_stmt(cpp_decl_stmt: CppDeclStatement, struct_name: str, options: LitgenOptions):
    r = ""
    for cpp_decl in cpp_decl_stmt.cpp_decls:
        r += _add_struct_member_decl(cpp_decl, struct_name, options)
    return r


def _add_public_struct_elements(public_zone: CppPublicProtectedPrivate, struct_name: str, options: LitgenOptions):
    r = ""
    for public_child in public_zone.block_children:
        if isinstance(public_child, CppDeclStatement):
            code = _add_struct_member_decl_stmt(cpp_decl_stmt=public_child, struct_name=struct_name, options=options)
            r += code
        # elif isinstance(public_child, CppEmptyLine):
        #     r += "\n"
        # elif isinstance(public_child, CppComment):
        #     r += code_utils.format_cpp_comment_multiline(public_child.cpp_element_comments.full_comment(), 4) + "\n"
        elif isinstance(public_child, CppFunctionDecl):
            code = _generate_method(
                function_infos=public_child,
                options=options,
                parent_struct_name=struct_name,
            )
            r = r + code
        elif isinstance(public_child, CppConstructorDecl):
            code = _generate_constructor(function_infos=public_child, options=options, parent_struct_name=struct_name)
            r = r + code
    return r


def _generate_struct_or_class(struct_infos: CppStruct, options: LitgenOptions) -> str:
    struct_name = struct_infos.class_name

    if struct_infos.is_templated_class():
        return ""

    _i_ = options.indent_cpp_spaces()

    comment = cpp_to_python.comment_pydef_one_line(struct_infos.cpp_element_comments.full_comment(), options)
    location = info_original_location_cpp(struct_infos, options)

    code_intro = ""
    code_intro += f"auto pyClass{struct_name} = py::class_<{struct_name}>{location}\n"
    code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'

    # code_intro += f'{_i_}.def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!

    if options.generate_to_string:
        code_outro = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }});'
    else:
        code_outro = f"{_i_};"

    r = code_intro

    if not struct_infos.has_non_default_ctor() and not struct_infos.has_deleted_default_ctor():
        r += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
    if struct_infos.has_deleted_default_ctor():
        r += f"{_i_}// (default constructor explicitly deleted)\n"

    for child in struct_infos.block.block_children:
        if child.tag() == "public":
            zone_code = _add_public_struct_elements(
                public_zone=cast(CppPublicProtectedPrivate, child), struct_name=struct_name, options=options
            )
            r += code_utils.indent_code(zone_code, indent_str=options.indent_cpp_spaces())
    r = r + code_outro
    r = r + "\n"
    return r


#################################
#           Namespace
################################
def _generate_namespace(
    cpp_namespace: CppNamespace,
    options: LitgenOptions,
    current_namespaces: List[str] = [],
) -> str:

    namespace_name = cpp_namespace.ns_name
    new_namespaces = current_namespaces + [namespace_name]
    namespace_code = generate_pydef(cpp_namespace.block, options, new_namespaces)
    location = info_original_location_cpp(cpp_namespace, options)

    namespace_code_commented = ""
    namespace_code_commented += f"// <namespace {namespace_name}>{location}\n"
    namespace_code_commented += namespace_code
    namespace_code_commented += f"// </namespace {namespace_name}>"

    namespace_code_commented += "\n"
    return namespace_code_commented


#################################
#           All
################################


def generate_boxed_types_binding_code(options: LitgenOptions):
    boxed_structs = cpp_to_python.BoxedImmutablePythonType.struct_codes()
    boxed_bindings = cpp_to_python.BoxedImmutablePythonType.binding_codes(options)
    if len(boxed_structs) > 0:
        boxed_inner_code = boxed_structs + "\n" + boxed_bindings
        boxed_inner_code = code_utils.unindent_code(boxed_inner_code)

        boxed_code = f"""

                // <Autogenerated_Boxed_Types>
                // Start
                {boxed_inner_code}// End
                // </Autogenerated Boxed Types>


                """
        boxed_code = code_utils.unindent_code(boxed_code)
        return boxed_code
    else:
        return ""


def generate_pydef(
    cpp_unit: Union[CppUnit, CppBlock],
    options: LitgenOptions,
    current_namespaces: List[str] = [],
    add_boxed_types_definitions: bool = False,
) -> str:

    line_spacer = _LineSpacer()
    code = ""
    for i, cpp_element in enumerate(cpp_unit.block_children):
        element_code = ""

        if False:
            pass
        elif isinstance(cpp_element, CppFunctionDecl) or isinstance(cpp_element, CppFunction):
            element_code = _generate_function(cpp_element, options, parent_struct_name="")
        elif isinstance(cpp_element, CppEnum):
            element_code = _generate_enum(cpp_element, options)
        elif isinstance(cpp_element, CppStruct) or isinstance(cpp_element, CppClass):
            element_code = _generate_struct_or_class(cpp_element, options)
        elif isinstance(cpp_element, CppNamespace):
            element_code = _generate_namespace(cpp_element, options, current_namespaces)

        if len(element_code) > 0:
            line_spacing = line_spacer.line_spaces(cpp_element)
            code += line_spacing + element_code

    if add_boxed_types_definitions:
        code = generate_boxed_types_binding_code(options) + code

    return code
