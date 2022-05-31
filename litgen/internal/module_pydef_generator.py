import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

from litgen.internal import srcml, CodeStyleOptions, cpp_to_python, code_utils
from litgen.internal.srcml.srcml_types import *

from function_wrapper_lambda import \
    make_function_wrapper_lambda, make_method_wrapper_lambda, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format

#################################
#           Enums
################################

def _generate_pydef_enum(enum: CppEnum, options: CodeStyleOptions) -> str:
    enum_type = enum.attribute_value("type")
    enum_name = enum.name

    code_intro = f'    py::enum_<{enum_name}>(m, "{enum_name}", py::arithmetic(),\n'

    comment = cpp_to_python.docstring_python_one_line(enum.cpp_element_comments.full_comment() , options)

    code_intro += f'        "{comment}")\n'
    code_inner = f'        .value("VALUE_NAME_PYTHON", VALUE_NAME_CPP, "(VALUE_COMMENT)")\n'
    code_outro = "    ;\n\n"
    final_code = code_intro

    def make_value_code(enum_decl: CppDecl):
        code = code_inner
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

    for child in enum.block.block_children:
        if child.tag() == "comment":
            final_code += f"        // {child.text()}\n"
        elif child.tag() == "decl":
            final_code = final_code + make_value_code(child)
        else:
            raise srcml.SrcMlException(child.srcml_element, f"Unexpected tag {child.tag()} in enum")
    final_code = final_code + code_outro
    return final_code


#################################
#           Functions
################################


def pyarg_code(function_infos: CppFunctionDecl, options: CodeStyleOptions) -> str:
    param_lines = []
    code_inner_defaultvalue = '    py::arg("ARG_NAME_PYTHON") = ARG_DEFAULT_VALUE'
    code_inner_nodefaultvalue = '    py::arg("ARG_NAME_PYTHON")'

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


def _generate_pydef_function(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> str:
    return_value_policy = _function_return_value_policy(function_infos)

    is_method = len(parent_struct_name) > 0

    fn_name_python = cpp_to_python.function_name_to_python(function_infos.name, options)

    code_intro = f'.def("{fn_name_python}",'
    if not is_method:
        code_intro = "m" + code_intro

    code_lines = [""]
    code_lines += [code_intro]
    lambda_code = make_function_wrapper_lambda(function_infos, options, parent_struct_name)
    lambda_code = code_utils.indent_code(lambda_code, 4)
    code_lines += lambda_code.split("\n")

    code_lines += pyarg_code(function_infos, options).split("\n")

    #  comment
    comment_cpp =  cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    code_lines += [f'    "{comment_cpp}"']

    # Return value policy
    if len(return_value_policy) > 0:
        code_lines[-1] += ","
        code_lines += [f"    pybind11::{return_value_policy}"]

    # Ending
    if is_method:
        code_lines += ")"
    else:
        code_lines += [');']
    code_lines += ["", ""]

    code = "\n".join(code_lines)
    code = code_utils.indent_code(code, options.indent_size_cpp_pydef)
    return code


#################################
#           Methods
################################


def _generate_pydef_constructor(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions) -> str:

    # Default constructors are always generated!
    if len(function_infos.parameter_list.parameters) == 0:
        return ""

    code = """
          .def(
              py::init<PARAMS>(),
              PYARGS
              "CONSTRUCTOR_DOC"
          )
    """

    pyarg_str = pyarg_code(function_infos, options)
    pyarg_str = code_utils.reindent_code(pyarg_str, 4, True)
    params_str = function_infos.parameter_list.types_only_for_template()

    code = code.replace("PARAMS", params_str)
    code = code.replace("PYARGS", pyarg_str)
    code = code.replace("CONSTRUCTOR_DOC",
                        cpp_to_python.docstring_python_one_line(
                            function_infos.cpp_element_comments.full_comment(), options))

    code = code_utils.unindent_code(code)
    code = code_utils.indent_code(code, 4)
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
    name_cpp = cpp_decl.name
    name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    comment = cpp_decl.cpp_element_comments.full_comment()

    code_inner_member  = f'    .def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT")\n'

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
        elif isinstance(public_child, CppEmptyLine):
            r += "\n"
        elif isinstance(public_child, CppComment):
            r += code_utils.format_cpp_comment_multiline(public_child.cpp_element_comments.full_comment(), 4) + "\n"
        elif isinstance(public_child, CppFunctionDecl):
            r = r + _generate_pydef_method(function_infos = public_child, options=options, parent_struct_name=struct_name)
        elif isinstance(public_child, CppConstructorDecl):
            r = r + _generate_pydef_constructor(function_infos = public_child, options=options)
    return r


def _generate_pydef_struct_or_class(struct_infos: CppStruct, options: CodeStyleOptions) -> str:
    struct_name = struct_infos.name

    code_intro  = f'auto pyClass{struct_name} = py::class_<{struct_name}>\n    (m, "{struct_name}", \n'
    comment = cpp_to_python.docstring_python_one_line(struct_infos.cpp_element_comments.full_comment(), options)
    code_intro += f'    "{comment}")\n\n'
    code_intro += f'    .def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!

    if options.generate_to_string:
        code_outro  = f'    .def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }}); \n\n'
    else:
        code_outro  = f'    ; \n\n'

    r = code_intro
    for child in struct_infos.block.block_children:
        if child.tag() == "public":
            r += _add_public_struct_elements(public_zone=child, struct_name=struct_name, options=options)
    r = r + code_outro

    r = code_utils.indent_code(r, 4)

    return r


#################################
#           All
################################

def generate_pydef(cpp_unit: CppUnit, options: CodeStyleOptions) -> str:
    r = ""
    for cpp_element in cpp_unit.block_children:
        if cpp_element.tag() == "enum":
            r += _generate_pydef_enum(cpp_element, options)
        elif cpp_element.tag() == "function" or cpp_element.tag() == "function_decl":
            r += _generate_pydef_function(cpp_element, options, parent_struct_name="")
        elif cpp_element.tag() == "struct" or cpp_element.tag() == "class":
            r += _generate_pydef_struct_or_class(cpp_element, options)
    return r