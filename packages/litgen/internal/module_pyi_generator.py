from typing import Union
import copy
import logging
import os, sys

_THIS_DIR = os.path.dirname(__file__)
sys.path = [_THIS_DIR + "/.."] + sys.path

from codemanip import code_utils, code_replacements

import srcmlcpp
from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_main
from srcmlcpp import srcml_warnings

from litgen import LitgenOptions
from litgen.internal import cpp_to_python
from litgen.internal.adapt_function import AdaptedFunction
from litgen.internal.adapt_function import make_adapted_function


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


def _add_stub_element(
    cpp_element: CppElementAndComment,
    first_code_line: str,
    options: LitgenOptions,
    body_lines: List[str] = [],
    fn_params_and_return: str = "",
) -> str:
    """Common layout for class, enum, and functions stubs"""

    location = cpp_to_python.info_original_location_python(cpp_element, options)
    first_line = first_code_line + location

    all_lines_except_first = []
    if len(fn_params_and_return) > 0:
        all_lines_except_first += fn_params_and_return.split("\n")
    all_lines_except_first += cpp_to_python.docstring_lines(cpp_element, options)
    all_lines_except_first += body_lines
    if len(body_lines) == 0:
        all_lines_except_first += ["pass"]

    _i_ = options.indent_python_spaces()
    all_lines_except_first = list(map(lambda s: _i_ + s, all_lines_except_first))

    all_lines_except_first = code_utils.align_python_comments_in_block_lines(all_lines_except_first)

    all_lines = [first_line] + all_lines_except_first
    all_lines = code_utils.strip_lines_right_space(all_lines)

    r = "\n".join(all_lines) + "\n"

    return r


def _make_decl_lines(cpp_decl: CppDecl, options: LitgenOptions) -> List[str]:
    var_name = cpp_to_python.decl_python_var_name(cpp_decl, options)
    var_value = cpp_to_python.decl_python_value(cpp_decl, options)

    lines = []

    decl_part = f"{var_name} = {var_value}"

    if cpp_to_python.python_shall_place_comment_at_end_of_line(cpp_decl, options):
        decl_line = decl_part + "  #" + cpp_to_python.python_comment_end_of_line(cpp_decl, options)
        lines.append(decl_line)
    else:
        comment_lines = cpp_to_python.python_comment_previous_lines(cpp_decl, options)
        lines += comment_lines
        lines.append(decl_part)

    return lines


def _make_enum_element_decl_lines(
    enum: CppEnum,
    enum_element_orig: CppDecl,
    previous_enum_element: Optional[CppDecl],
    options: LitgenOptions,
) -> List[str]:

    enum_element = copy.deepcopy(enum_element_orig)

    if cpp_to_python.enum_element_is_count(enum, enum_element, options):
        return []

    if len(enum_element.initial_value_code) == 0:
        if previous_enum_element is None:
            # the first element of an enum has a default value of 0
            enum_element.initial_value_code = "0"
            enum_element_orig.initial_value_code = enum_element.initial_value_code
        else:
            try:
                previous_value = int(previous_enum_element.initial_value_code)
                enum_element.initial_value_code = str(previous_value + 1)
                enum_element_orig.initial_value_code = enum_element.initial_value_code
            except ValueError:
                srcml_warnings.emit_srcml_warning(
                    enum_element.srcml_element,
                    """
                        Cannot compute the value of an enum element (previous element value is not an int), it was skipped!
                        """,
                    options.srcml_options,
                )
                return []

    enum_element.decl_name = cpp_to_python.enum_value_name_to_python(enum, enum_element, options)

    #
    # Sometimes, enum decls have interdependent values like this:
    #     enum MyEnum {
    #         MyEnum_a = 1, MyEnum_b,
    #         MyEnum_foo = MyEnum_a | MyEnum_b    //
    #     };
    #
    # So, we search and replace enum strings in the default value (.init)
    #
    for enum_decl in enum.get_enum_decls():
        enum_decl_cpp_name = enum_decl.decl_name
        enum_decl_python_name = cpp_to_python.enum_value_name_to_python(enum, enum_decl, options)

        replacement = code_replacements.StringReplacement()
        replacement.replace_what = r"\b" + enum_decl_cpp_name + r"\b"
        replacement.by_what = f"Literal[{enum.enum_name}.{enum_decl_python_name}]"
        enum_element.initial_value_code = code_replacements.apply_one_replacement(
            enum_element.initial_value_code, replacement
        )
        # enum_element.init = enum_element.init.replace(enum_decl_cpp_name, enum_decl_python_name)
        # code_utils.w

    return _make_decl_lines(enum_element, options)


#################################
#           Enums
################################


def _generate_pyi_enum(enum: CppEnum, options: LitgenOptions) -> str:
    first_code_line = f"class {enum.enum_name}(Enum):"

    body_lines: List[str] = []

    previous_enum_element: Optional[CppDecl] = None
    for child in enum.block.block_children:
        if isinstance(child, CppDecl):
            body_lines += _make_enum_element_decl_lines(enum, child, previous_enum_element, options)
            previous_enum_element = child
        if isinstance(child, CppEmptyLine) and options.python_keep_empty_lines:
            body_lines.append("")
        if isinstance(child, CppComment):
            body_lines += cpp_to_python.python_comment_previous_lines(child, options)
    r = _add_stub_element(enum, first_code_line, options, body_lines)
    return r


#################################
#           Functions
################################


def _generate_pyi_function(
    function_infos: CppFunctionDecl,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> str:
    adapted_function = make_adapted_function(function_infos, options, parent_struct_name)

    r = _generate_pyi_function_impl(adapted_function, options, parent_struct_name)
    return r


def _paramlist_call_strs(param_list: CppParameterList, options: LitgenOptions) -> List[str]:
    r = []
    for param in param_list.parameters:
        param_name_python = cpp_to_python.var_name_to_python(param.decl.decl_name, options)
        param_type_cpp = param.decl.cpp_type.str_code()
        param_type_python = cpp_to_python.type_to_python(param_type_cpp, options)
        param_default_value = cpp_to_python.default_value_to_python(param.default_value(), options)

        param_code = f"{param_name_python}: {param_type_python}"
        if len(param_default_value) > 0:
            param_code += f" = {param_default_value}"

        r.append(param_code)
    return r


def _generate_pyi_function_impl(
    adapted_function: AdaptedFunction,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> str:

    function_infos = adapted_function.function_infos

    function_name_python = cpp_to_python.function_name_to_python(function_infos.function_name, options)

    return_type_python = cpp_to_python.type_to_python(function_infos.full_return_type(options.srcml_options), options)

    first_code_line = f"def {function_name_python}("

    params_strs = _paramlist_call_strs(function_infos.parameter_list, options)
    return_line = f") -> {return_type_python}:"

    # Try to add all params and return type on the same line
    def all_on_one_line():
        first_code_line_full = first_code_line
        first_code_line_full += ", ".join(params_strs)
        first_code_line_full += return_line
        if len(first_code_line_full) < options.python_max_line_length:
            return first_code_line_full
        else:
            return None

    if all_on_one_line() is not None:
        first_code_line = all_on_one_line()
        params_and_return_str = ""
    else:
        params_and_return_str = ",\n".join(params_strs) + "\n" + return_line

    body_lines: List[str] = []

    r = _add_stub_element(function_infos, first_code_line, options, body_lines, params_and_return_str)

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
        elif isinstance(public_child, CppEmptyLine) and options.python_keep_empty_lines:
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
def _generate_pyi_namespace(cpp_namespace: CppNamespace, options: LitgenOptions, current_namespaces=None) -> str:

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
        if isinstance(child, CppEmptyLine) and options.python_keep_empty_lines:
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
