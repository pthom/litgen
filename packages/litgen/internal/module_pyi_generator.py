from typing import List, Optional, Union

from codemanip import code_utils
from litgen.internal import cpp_to_python
from litgen.internal.adapted_types_wip.adapted_types import *
from litgen.options import LitgenOptions
from srcmlcpp.srcml_types import *


#################################
#           Utilities
################################


def _add_new_lines(code: str, nb_lines_before: int = 0, nb_lines_after: int = 1) -> str:
    r = "\n" * nb_lines_before + code + "\n" * nb_lines_after
    return r


def _add_one_line_before(code: str, options: LitgenOptions) -> str:
    if options.srcml_options.preserve_empty_lines:
        return code
    else:
        return _add_new_lines(code, nb_lines_before=1)


def _add_two_lines_before(code: str, options: LitgenOptions) -> str:
    if options.srcml_options.preserve_empty_lines:
        return code
    else:
        return _add_new_lines(code, nb_lines_before=2, nb_lines_after=0)


#################################
#           Enums
################################


def _generate_pyi_enum(enum: CppEnum, options: LitgenOptions) -> str:
    adapted_enum = AdaptedEnum(enum, options)
    r = adapted_enum.str_stub()
    return r


#################################
#           Functions
################################


def _generate_pyi_function(
    function_infos: CppFunctionDecl,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> str:

    adapted_function = AdaptedFunction(function_infos, parent_struct_name, options)
    r = adapted_function.str_stub()
    return r


#################################
#           Methods
################################


def _generate_pyi_constructor(function_infos: CppFunctionDecl, options: LitgenOptions) -> str:
    return ""

    # if "delete" in function_infos.specifiers:
    #     return ""
    #
    # """
    # A constructor decl look like this
    #     .def(py::init<ARG_TYPES_LIST>(),
    #     PY_ARG_LIST
    #     DOC_STRING);
    # """
    #
    # _i_ = options.indent_python_spaces()
    #
    # params_str = function_infos.parameter_list.types_only_for_template()
    # doc_string = cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    # location = cpp_to_python.info_original_location_python(function_infos, options)
    #
    # code_lines = []
    # code_lines.append(f".def(py::init<{params_str}>(){location}")
    # code_lines += pyarg_code_list(function_infos, options)
    # if len(doc_string) > 0:
    #     code_lines.append(f'"{doc_string}"')
    #
    # # indent lines after first
    # for i in range(1, len(code_lines)):
    #     code_lines[i] = _i_ + code_lines[i]
    #
    # code_lines[-1] = code_utils.add_item_before_comment(code_lines[-1], ")")
    #
    # code = code_utils.join_lines_with_token_before_comment(code_lines, ",")
    # code += "\n"
    #
    # return code


def _generate_pyi_method(function_infos: CppFunctionDecl, options: LitgenOptions, parent_struct_name: str) -> str:

    return ""

    if function_infos.decl_name == parent_struct_name:
        # Sometimes, srcml might see a constructor as a decl
        # Example:
        # struct Foo
        # {
        #     IMGUI_API Foo();
        # };
        return _generate_pyi_constructor(function_infos, options)
    else:
        return _generate_pyi_function(function_infos, options, parent_struct_name)


#################################
#           Structs and classes
################################


def _add_struct_member_decl(cpp_decl: CppDecl, struct_name: str, options: LitgenOptions) -> str:

    return ""

    # _i_ = options.indent_python_spaces()
    # name_cpp = cpp_decl.decl_name
    # name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    # comment = cpp_decl.cpp_element_comments.full_comment()
    # location = info_cpp_element_original_location(cpp_decl, options)
    #
    # if len(cpp_decl.range) > 0:
    #     # We ignore bitfields
    #     return ""
    #
    # if cpp_decl.is_c_array_fixed_size():
    #     # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11
    #     array_typename = cpp_decl.cpp_type.str_code()
    #     if array_typename not in options.c_array_numeric_member_types:
    #         srcml_warnings.emit_srcml_warning(
    #             cpp_decl.srcml_element,
    #             """
    #             Only numeric C Style arrays are supported
    #                 Hint: use a vector, or extend `options.c_array_numeric_member_types`
    #             """,
    #             options.srcml_options,
    #         )
    #         return ""
    #
    #     elif not options.c_array_numeric_member_flag_replace:
    #         srcml_warnings.emit_srcml_warning(
    #             cpp_decl.srcml_element,
    #             """
    #             Detected a numeric C Style array, but will not export it.
    #                 Hint: set `options.c_array_numeric_member_flag_replace = True`
    #             """,
    #             options.srcml_options,
    #         )
    #         return ""
    #
    #     array_size = cpp_decl.c_array_size()
    #
    #     if array_size is None:
    #         array_size_str = cpp_decl.c_array_size_str()
    #         if array_size_str in options.c_array_numeric_member_size_dict.keys():
    #             array_size = options.c_array_numeric_member_size_dict[array_size_str]
    #             if type(array_size) != int:
    #                 srcml_warnings.emit_srcml_warning(
    #                     cpp_decl.srcml_element,
    #                     """
    #                     options.c_array_numeric_member_size_dict should contains [str,int] items !
    #                     """,
    #                     options.srcml_options,
    #                 )
    #                 return ""
    #         else:
    #             srcml_warnings.emit_srcml_warning(
    #                 cpp_decl.srcml_element,
    #                 f"""
    #                 Detected a numeric C Style array, but will not export it because its size is not parsable.
    #                     Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
    #                 """,
    #                 options.srcml_options,
    #             )
    #             return ""
    #
    #     template_code = f"""
    #         .def_property("{name_python}",
    #             []({struct_name} &self) -> pybind11::array
    #             {{
    #                 auto dtype = pybind11::dtype(pybind11::format_descriptor<{array_typename}>::format());
    #                 auto base = pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}});
    #                 return pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}}, self.{name_cpp}, base);
    #             }}, []({struct_name}& self) {{}})
    #     """
    #
    #     r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True) + "\n"
    #     return r
    #
    # else:
    #     code_inner_member = (
    #         f'.def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT"){location}\n'
    #     )
    #     r = code_inner_member
    #     r = r.replace("MEMBER_NAME_PYTHON", name_python)
    #     r = r.replace("MEMBER_NAME_CPP", name_cpp)
    #     r = r.replace("MEMBER_COMMENT", cpp_to_python.docstring_python_one_line(comment, options))
    #     return r


def _add_struct_member_decl_stmt(cpp_decl_stmt: CppDeclStatement, struct_name: str, options: LitgenOptions):
    return ""

    r = ""
    for cpp_decl in cpp_decl_stmt.cpp_decls:
        r += _add_struct_member_decl(cpp_decl, struct_name, options)
    return r


def _add_public_struct_elements(public_zone: CppPublicProtectedPrivate, struct_name: str, options: LitgenOptions):
    return ""

    r = ""
    for public_child in public_zone.block_children:
        if isinstance(public_child, CppDeclStatement):
            code = _add_struct_member_decl_stmt(cpp_decl_stmt=public_child, struct_name=struct_name, options=options)
            r += code
        elif isinstance(public_child, CppEmptyLine) and options.python_reproduce_cpp_layout:
            r += "\n"
        # elif isinstance(public_child, CppComment):
        #     r += code_utils.format_cpp_comment_multiline(public_child.cpp_element_comments.full_comment(), 4) + "\n"
        elif isinstance(public_child, CppFunctionDecl):
            code = _generate_pyi_method(
                function_infos=public_child,
                options=options,
                parent_struct_name=struct_name,
            )
            r = r + code
        elif isinstance(public_child, CppConstructorDecl):
            code = _generate_pyi_constructor(function_infos=public_child, options=options)
            r = r + code
    return r


def _generate_pyi_struct_or_class(struct_infos: CppStruct, options: LitgenOptions) -> str:
    return ""

    # struct_name = struct_infos.name
    #
    # if struct_infos.template is not None:
    #     return ""
    #
    # _i_ = options.indent_python_spaces()
    #
    # comment = cpp_to_python.docstring_python_one_line(struct_infos.cpp_element_comments.full_comment(), options)
    # location = info_cpp_element_original_location(struct_infos, options)
    #
    # code_intro = ""
    # code_intro += f"auto pyClass{struct_name} = py::class_<{struct_name}>{location}\n"
    # code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'
    #
    # # code_intro += f'{_i_}.def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!
    #
    # if options.generate_to_string:
    #     code_outro = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }});'
    # else:
    #     code_outro = f"{_i_};"
    #
    # r = code_intro
    #
    # if not struct_infos.has_non_default_ctor() and not struct_infos.has_deleted_default_ctor():
    #     r += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
    # if struct_infos.has_deleted_default_ctor():
    #     r += f"{_i_}// (default constructor explicitly deleted)\n"
    #
    # for child in struct_infos.block.block_children:
    #     if child.tag() == "public":
    #         zone_code = _add_public_struct_elements(public_zone=child, struct_name=struct_name, options=options)
    #         r += code_utils.indent_code(zone_code, indent_str=options.indent_python_spaces())
    # r = r + code_outro
    # r = r + "\n"
    # return r


#################################
#           Namespace
################################
def _generate_pyi_namespace(
    cpp_namespace: CppNamespace, options: LitgenOptions, current_namespaces: Optional[List[str]] = None
) -> str:

    if current_namespaces is None:
        current_namespaces = []

    namespace_name = cpp_namespace.ns_name
    new_namespaces = current_namespaces + [namespace_name]
    namespace_code = generate_pyi(cpp_namespace.block, options, new_namespaces)
    location = cpp_to_python.info_original_location_python(cpp_namespace, options)

    namespace_code_commented = ""
    namespace_code_commented += f"# <namespace {namespace_name}>{location}\n"
    namespace_code_commented += namespace_code
    namespace_code_commented += f"# </namespace {namespace_name}>"

    namespace_code_commented += "\n"
    return namespace_code_commented


#################################
#           All
################################


def generate_pyi(
    cpp_unit: Union[CppUnit, CppBlock],
    options: LitgenOptions,
    current_namespaces: List[str] = [],
    add_boxed_types_definitions: bool = False,
) -> str:

    r = ""
    for i, child in enumerate(cpp_unit.block_children):
        if False:
            pass
        if isinstance(child, CppEmptyLine) and options.python_reproduce_cpp_layout:
            r += "\n"
        if isinstance(child, CppComment):
            r += "\n".join(cpp_to_python.python_comment_previous_lines(child, options)) + "\n"
        elif isinstance(child, CppFunctionDecl) or isinstance(child, CppFunction):
            r += _add_one_line_before(_generate_pyi_function(child, options, parent_struct_name=""), options)
        elif isinstance(child, CppEnum):
            r += _add_two_lines_before(_generate_pyi_enum(child, options), options)
        elif isinstance(child, CppStruct) or isinstance(child, CppClass):
            r += _add_two_lines_before(_generate_pyi_struct_or_class(child, options), options)
        elif isinstance(child, CppNamespace):
            r += _add_two_lines_before(_generate_pyi_namespace(child, options, current_namespaces), options)

    if add_boxed_types_definitions:
        pass
        # boxed_structs = cpp_to_python.BoxedImmutablePythonType.struct_codes()
        # boxed_bindings = cpp_to_python.BoxedImmutablePythonType.binding_codes(options)
        # if len(boxed_structs) > 0:
        #     r = boxed_structs + "\n" + boxed_bindings + "\n" + r

    r = code_utils.code_set_max_consecutive_empty_lines(r, options.python_max_consecutive_empty_lines)
    return r
