import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import srcmlcpp
from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_main

from litgen import CodeStyleOptions
from litgen.internal import cpp_to_python, code_utils
from litgen.internal.function_wrapper_lambda import \
    make_function_wrapper_lambda, make_method_wrapper_lambda, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format


#################################
#           Enums
################################

def _generate_pydef_enum(enum: CppEnum, options: CodeStyleOptions) -> str:
    enum_type = enum.attribute_value("type")
    enum_name = enum.name

    _i_ = options.indent_cpp_spaces()
    comment = cpp_to_python.docstring_python_one_line(enum.cpp_element_comments.full_comment() , options)

    code_intro = f'py::enum_<{enum_name}>(m, "{enum_name}", py::arithmetic(), "{comment}")\n'

    def make_value_code(enum_decl: CppDecl):
        code = f'{_i_}.value("VALUE_NAME_PYTHON", VALUE_NAME_CPP, "VALUE_COMMENT")\n'

        value_name_cpp = enum_decl.name
        value_name_python = cpp_to_python.enum_value_name_to_python(enum_name, value_name_cpp, options)

        if enum_type == "class":
            value_name_cpp_str = enum_name + "::" + value_name_cpp
        else:
            value_name_cpp_str = value_name_cpp

        code = code.replace("VALUE_NAME_PYTHON", value_name_python)
        code = code.replace("VALUE_NAME_CPP", value_name_cpp_str)
        code = code.replace("VALUE_COMMENT", code_utils.format_cpp_comment_on_one_line(
            enum_decl.cpp_element_comments.full_comment()))

        if cpp_to_python.enum_value_name_is_count(enum_name, value_name_cpp, options):
            return ""
        return code

    result = code_intro
    for i, child in enumerate(enum.block.block_children):
        if child.tag() == "comment":
            result += code_utils.format_cpp_comment_multiline(
                child.text(), indentation_str=options.indent_cpp_spaces()) + "\n"
        elif child.tag() == "decl":
            result += make_value_code(child)
        else:
            raise srcmlcpp.SrcMlException(child.srcml_element, f"Unexpected tag {child.tag()} in enum")
    result = result[:-1] + ";\n"
    return result


#################################
#           Functions
################################


def pyarg_code(function_infos: CppFunctionDecl, options: CodeStyleOptions) -> str:
    _i_ = options.indent_cpp_spaces()

    param_lines = []
    code_inner_defaultvalue = f'py::arg("ARG_NAME_PYTHON") = ARG_DEFAULT_VALUE'
    code_inner_nodefaultvalue = f'py::arg("ARG_NAME_PYTHON")'

    for idx_param, param in enumerate(function_infos.parameter_list.parameters):
        param_default_value = param.default_value()
        if len(param_default_value) > 0:
            if is_default_sizeof_param(param, options):
                default_value_cpp = "-1"
            else:
                default_value_cpp = param_default_value
            param_line = code_inner_defaultvalue \
                .replace("ARG_NAME_PYTHON", cpp_to_python.var_name_to_python(param.variable_name(), options)) \
                .replace("ARG_DEFAULT_VALUE", default_value_cpp)
        else:
            if is_buffer_size_name_at_idx(function_infos.parameter_list, options, idx_param):
                continue
            if  is_param_variadic_format(function_infos.parameter_list, options, idx_param):
                continue
            param_line= code_inner_nodefaultvalue.replace("ARG_NAME_PYTHON",
                                                          cpp_to_python.var_name_to_python(param.variable_name(), options))

        param_lines.append(param_line)

    code = ",\n".join(param_lines)
    if len(param_lines) > 0:
        code += ","
    return code


def pyarg_code_list(function_infos: CppFunctionDecl, options: CodeStyleOptions) -> List[str]:
    code = pyarg_code(function_infos, options)
    if len(code) == 0:
        return []
    lines = code.split("\n")
    r = []
    for line in lines:
        if line.endswith(","):
            line = line[:-1]
        r.append(line)
    return r


def _function_return_value_policy(function_infos: CppFunctionDecl) -> str:
    """Parses the return_value_policy from the function end of line comment
    For example:
        // A static instance (which python shall not delete, as enforced by the marker return_policy below)
        static Foo& Instance() { static Foo instance; return instance; }       // return_value_policy::reference
    """
    token = "return_value_policy::"
    eol_comment = function_infos.cpp_element_comments.eol_comment_code()
    if "return_value_policy::" in eol_comment:
        return_value_policy = eol_comment[ eol_comment.index(token) + len(token) : ]
        return return_value_policy
    else:
        return ""


def info_cpp_element_original_location(cpp_element: CppElement, options: CodeStyleOptions):
    if not options.flag_show_original_location_in_pybind_file:
        return ""
    _i_ = options.indent_cpp_spaces()
    header_file = srcml_main.srcml_main_context().current_parsed_file
    line = cpp_element.start().line
    r = f"{_i_}// {header_file}:{line}"
    return r


def _generate_pydef_function(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> str:

    _i_ = options.indent_cpp_spaces()

    return_value_policy = _function_return_value_policy(function_infos)

    is_method = len(parent_struct_name) > 0

    fn_name_python = cpp_to_python.function_name_to_python(function_infos.name, options)

    module_str = "" if is_method else "m"

    code_lines: List[str] = []
    code_lines += [f'{module_str}.def("{fn_name_python}",']
    lambda_code = make_function_wrapper_lambda(function_infos, options, parent_struct_name)
    lambda_code = code_utils.indent_code(lambda_code, indent_str=_i_)
    code_lines += lambda_code.split("\n")

    pyarg_str = code_utils.indent_code(pyarg_code(function_infos, options),indent_str=options.indent_cpp_spaces())
    if len(pyarg_str) > 0:
        code_lines += pyarg_str.split("\n")

    #  comment
    comment_cpp =  cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    if len(comment_cpp) == 0:
        # remove last "," from last line since there is no comment that follows
        if code_lines[-1].endswith(","):
            code_lines[-1] = code_lines[-1][ : -1]
    else:
        code_lines += [f'{_i_}"{comment_cpp}"']

    # Return value policy
    if len(return_value_policy) > 0:
        code_lines[-1] += ","
        code_lines += [f"{_i_}pybind11::return_value_policy::{return_value_policy}"]

    # Ending
    if is_method:
        code_lines += ")"
    else:
        code_lines += [');']

    code = "\n".join(code_lines)
    return code


#################################
#           Methods
################################


def _generate_pydef_constructor(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions) -> str:

    if "delete" in function_infos.specifiers:
        return ""

    """
    A constructor decl look like this
        .def(py::init<ARG_TYPES_LIST>(),
        PY_ARG_LIST
        DOC_STRING);    
    """

    _i_ = options.indent_cpp_spaces()

    params_str = function_infos.parameter_list.types_only_for_template()
    doc_string = cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)

    code_lines = []
    code_lines.append(f".def(py::init<{params_str}>()")
    code_lines += pyarg_code_list(function_infos, options)
    if len(doc_string) > 0:
        code_lines.append(f'"{doc_string}"')

    # indent lines after first
    for i in range(1, len(code_lines)):
        code_lines[i] = _i_ + code_lines[i]

    code = ",\n".join(code_lines)
    code += ")"
    return code


def _generate_pydef_method(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str) -> str:
    return _generate_pydef_function(function_infos, options, parent_struct_name)


#################################
#           Structs and classes
################################


def _add_struct_member_decl(cpp_decl: CppDecl, struct_name: str, options: CodeStyleOptions):
    _i_ = options.indent_cpp_spaces()
    name_cpp = cpp_decl.name
    name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    comment = cpp_decl.cpp_element_comments.full_comment()

    code_inner_member  = f'.def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT")\n'

    r = code_inner_member
    r = r.replace("MEMBER_NAME_PYTHON",  name_python)
    r = r.replace("MEMBER_NAME_CPP", name_cpp)
    r = r.replace("MEMBER_COMMENT", cpp_to_python.docstring_python_one_line(comment, options))
    return r


def _add_struct_member_decl_stmt(cpp_decl_stmt: CppDeclStatement, struct_name: str, options: CodeStyleOptions):
    r = ""
    for cpp_decl in cpp_decl_stmt.cpp_decls:
        r += _add_struct_member_decl(cpp_decl, struct_name, options)
    return r


def _add_public_struct_elements(public_zone: CppPublicProtectedPrivate, struct_name: str, options: CodeStyleOptions):
    r = ""
    for public_child in public_zone.block_children:
        if isinstance(public_child, CppDeclStatement):
            r += _add_struct_member_decl_stmt(cpp_decl_stmt=public_child, struct_name=struct_name, options=options)
        # elif isinstance(public_child, CppEmptyLine):
        #     r += "\n"
        # elif isinstance(public_child, CppComment):
        #     r += code_utils.format_cpp_comment_multiline(public_child.cpp_element_comments.full_comment(), 4) + "\n"
        elif isinstance(public_child, CppFunctionDecl):
            r = r + _generate_pydef_method(function_infos = public_child, options=options, parent_struct_name=struct_name) + "\n"
        elif isinstance(public_child, CppConstructorDecl):
            r = r + _generate_pydef_constructor(function_infos = public_child, options=options) + "\n"
    return r


def _generate_pydef_struct_or_class(struct_infos: CppStruct, options: CodeStyleOptions) -> str:
    struct_name = struct_infos.name

    _i_ = options.indent_cpp_spaces()

    comment = cpp_to_python.docstring_python_one_line(struct_infos.cpp_element_comments.full_comment(), options)

    code_intro = ""
    code_intro += f'auto pyClass{struct_name} = py::class_<{struct_name}>\n'
    code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'

    # code_intro += f'{_i_}.def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!

    if options.generate_to_string:
        code_outro  = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }}); \n'
    else:
        code_outro  = f'{_i_}; \n'

    r = code_intro

    if not struct_infos.has_non_default_ctor() and not struct_infos.has_deleted_default_ctor():
        r += f"{_i_}.def(py::init<>() // implicit default constructor\n"
    if struct_infos.has_deleted_default_ctor():
        r += f"{_i_}// (default constructor explicitly deleted)\n"

    for child in struct_infos.block.block_children:
        if child.tag() == "public":
            zone_code = _add_public_struct_elements(public_zone=child, struct_name=struct_name, options=options)
            r += code_utils.indent_code(zone_code, indent_str=options.indent_cpp_spaces())
    r = r + code_outro

    return r


#################################
#           Namespace
################################
def _generate_pydef_namespace(
        cpp_namespace: CppNamespace,
        options: CodeStyleOptions,
        current_namespaces: List[str] = []) -> str:

    namespace_name = cpp_namespace.name
    new_namespaces = current_namespaces + [namespace_name]
    namespace_code = generate_pydef(cpp_namespace.block, options, new_namespaces)

    namespace_code_commented = ""
    namespace_code_commented += f"// <namespace {namespace_name}>\n"
    namespace_code_commented += namespace_code
    namespace_code_commented += f"// </namespace {namespace_name}>\n"

    return namespace_code_commented


#################################
#           All
################################


def _add_new_lines(code: str, nb_lines_before: int = 0, nb_lines_after: int = 1) -> str:
    r = "\n" * nb_lines_before + code + "\n" * nb_lines_after
    return r


def _add_one_line_after(code: str) -> str:
    return _add_new_lines(code, nb_lines_after=1)


def _add_one_line_before_two_after(code: str) -> str:
    return _add_new_lines(code, nb_lines_before=1, nb_lines_after=2)


def generate_pydef(cpp_unit: CppUnit, options: CodeStyleOptions, current_namespaces: List[str] = []) -> str:

    r = ""
    indent_level = 0
    for i, cpp_element in enumerate(cpp_unit.block_children):
        if False:
            pass
        elif isinstance(cpp_element, CppFunctionDecl) or isinstance(cpp_element, CppFunction):
            r += _add_one_line_after( _generate_pydef_function(cpp_element, options, parent_struct_name="") )
        elif isinstance(cpp_element, CppEnum):
            r += _add_one_line_before_two_after( _generate_pydef_enum(cpp_element, options) )
        elif isinstance(cpp_element, CppStruct) or isinstance(cpp_element, CppClass):
            r += _add_one_line_before_two_after( _generate_pydef_struct_or_class(cpp_element, options) )
        elif isinstance(cpp_element, CppStruct) or isinstance(cpp_element, CppNamespace):
            r += _add_one_line_before_two_after( _generate_pydef_namespace(cpp_element, options, current_namespaces) )
    return r
