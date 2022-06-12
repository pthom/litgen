import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import logging

import srcmlcpp
from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_main
from srcmlcpp import srcml_warnings

from litgen import CodeStyleOptions
from litgen.internal import cpp_to_python, code_utils, code_replacements
from litgen.internal.cpp_function_adapted_params import CppFunctionDeclWithAdaptedParams
from litgen.internal.function_params_adapter import make_function_params_adapter
from litgen.internal.function_wrapper_lambda import \
    make_function_wrapper_lambda_impl, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format


def _add_new_lines(code: str, nb_lines_before: int = 0, nb_lines_after: int = 1) -> str:
    r = "\n" * nb_lines_before + code + "\n" * nb_lines_after
    return r


def _add_one_line_before(code: str) -> str:
    return _add_new_lines(code, nb_lines_before=1)


def _add_two_lines_before(code: str) -> str:
    return _add_new_lines(code, nb_lines_before=2, nb_lines_after=0)


def _add_stub_element(
        cpp_element: CppElementAndComment,
        first_code_line: str,
        options: CodeStyleOptions,
        body_lines: List[str] = []
    ) -> str:
    """Common layout for class, enum, and functions stubs"""

    location = cpp_to_python.info_original_location_python(cpp_element, options)
    all_lines = [first_code_line + location]

    doc_lines = cpp_to_python.docstring_lines(cpp_element, options)

    remaining_lines = doc_lines + body_lines
    if len(body_lines) == 0:
        remaining_lines.append("pass")

    _i_ = options.indent_python_spaces()
    remaining_lines = list(map(lambda s: _i_ + s, remaining_lines))

    all_lines += remaining_lines

    r = "\n".join(all_lines) + "\n"

    return r


def _make_decl_lines(cpp_decl: CppDecl, options: CodeStyleOptions) -> List[str]:
    var_name = cpp_to_python.decl_python_var_name(cpp_decl, options)
    var_value = cpp_to_python.decl_python_value(cpp_decl, options)
    comment_lines = cpp_to_python.python_comment_lines(cpp_decl, options)

    r = []

    flag_comment_first = cpp_to_python.python_comment_place_on_previous_lines(cpp_decl, options)

    if flag_comment_first:
        r += comment_lines

    decl_line = f"{var_name} = {var_value}"
    if not flag_comment_first:
        decl_line += options.indent_python_spaces() + comment_lines[0]

    r.append(decl_line)

    return r


def _make_enum_element_decl_lines(
        enum: CppEnum,
        enum_element: CppDecl,
        previous_enum_element: CppDecl,
        options: CodeStyleOptions) -> List[str]:

    if cpp_to_python.enum_element_is_count(enum, enum_element, options):
        return []

    if len(enum_element.init) == 0:

        if previous_enum_element is None:
            srcml_warnings.emit_srcml_warning(enum_element.srcml_element, """
                    Cannot compute the value of an enum element (previous element missing), it was skipped!
                    """, options.srcml_options)
            return []

        try:
            previous_value = int(previous_enum_element.init)
            enum_element.init = str(previous_value + 1)
        except ValueError:
            srcml_warnings.emit_srcml_warning(enum_element.srcml_element, """
                    Cannot compute the value of an enum element (previous element value is not an int), it was skipped!
                    """, options.srcml_options)
            return []

    enum_element.name = cpp_to_python.enum_value_name_to_python(enum, enum_element, options)
    return _make_decl_lines(enum_element, options)



#################################
#           Enums
################################

def _generate_pyi_enum(enum: CppEnum, options: CodeStyleOptions) -> str:

    enum_name = enum.name

    _i_ = options.indent_python_spaces()

    first_code_line = f"class {enum_name}(Enum):"

    body_lines: List[str] = []

    previous_enum_element: CppDecl = None
    for child in enum.block.block_children:
        if isinstance(child, CppDecl):
            body_lines += _make_enum_element_decl_lines(enum, child, previous_enum_element, options)
            previous_enum_element = child
        if isinstance(child, CppEmptyLine):
            body_lines.append("")
        if isinstance(child, CppComment):
            body_lines += cpp_to_python.python_comment_lines(child, options)
    r = _add_stub_element(enum, first_code_line, options, body_lines)
    return r

    # _i_ = options.indent_python_spaces()
    # comment = cpp_to_python.docstring_python_one_line(enum.cpp_element_comments.full_comment() , options)
    # location = info_cpp_element_original_location(enum, options)
    #
    # code_intro = f'py::enum_<{enum_name}>(m, "{enum_name}", py::arithmetic(), "{comment}"){location}\n'
    #
    # def make_value_code(enum_decl: CppDecl):
    #     code = f'{_i_}.value("VALUE_NAME_PYTHON", VALUE_NAME_CPP, "VALUE_COMMENT")\n'
    #
    #     value_name_cpp = enum_decl.name
    #     value_name_python = cpp_to_python.enum_value_name_to_python(enum_name, value_name_cpp, options)
    #
    #     if enum_type == "class":
    #         value_name_cpp_str = enum_name + "::" + value_name_cpp
    #     else:
    #         value_name_cpp_str = value_name_cpp
    #
    #     code = code.replace("VALUE_NAME_PYTHON", value_name_python)
    #     code = code.replace("VALUE_NAME_CPP", value_name_cpp_str)
    #     code = code.replace("VALUE_COMMENT", code_utils.format_cpp_comment_on_one_line(
    #         enum_decl.cpp_element_comments.full_comment()))
    #
    #     if cpp_to_python.enum_value_name_is_count(enum_name, value_name_cpp, options):
    #         return ""
    #     return code
    #
    # result = code_intro
    # for i, child in enumerate(enum.block.block_children):
    #     if child.tag() == "comment":
    #         result += code_utils.format_cpp_comment_multiline(
    #             child.text(), indentation_str=options.indent_python_spaces()) + "\n"
    #     elif child.tag() == "decl":
    #         result += make_value_code(child)
    #     else:
    #         raise srcmlcpp.SrcMlException(child.srcml_element, f"Unexpected tag {child.tag()} in enum")
    # result = result[:-1]
    # result = code_utils.add_item_before_comment(result, ";")
    # return result


#################################
#           Functions
################################


def pyarg_code(function_infos: CppFunctionDecl, options: CodeStyleOptions) -> str:
    return ""

    _i_ = options.indent_python_spaces()

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

    code = code_utils.join_lines_with_token_before_comment(param_lines, ",")
    if len(param_lines) > 0:
        code += ","
    return code


def pyarg_code_list(function_infos: CppFunctionDecl, options: CodeStyleOptions) -> List[str]:
    return ""

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
    return ""

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
    return ""

    if not options.original_location_flag_show:
        return ""
    _i_ = options.indent_python_spaces()
    header_file = srcml_main.srcml_main_context().current_parsed_file
    line = cpp_element.start().line
    r = f"{_i_}// {header_file}:{line}"
    return r


def _generate_pyi_function(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
) -> str:
    return ""

    function_adapted_params = make_function_params_adapter(function_infos, options, parent_struct_name)

    r = ""
    r += _generate_pyi_function_impl(function_adapted_params, options, parent_struct_name)
    return r


def _generate_pyi_function_impl(
        function_adapted_params: CppFunctionDeclWithAdaptedParams,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> str:
    return ""


    _i_ = options.indent_python_spaces()

    function_infos = function_adapted_params.function_infos
    return_value_policy = _function_return_value_policy(function_infos)

    is_method = len(parent_struct_name) > 0

    fn_name_python = cpp_to_python.function_name_to_python(function_infos.name, options)
    location = info_cpp_element_original_location(function_infos, options)

    module_str = "" if is_method else "m"

    code_lines: List[str] = []
    code_lines += [f'{module_str}.def("{fn_name_python}",{location}']
    lambda_code = make_function_wrapper_lambda_impl(function_adapted_params, options, parent_struct_name)
    lambda_code = code_utils.indent_code(lambda_code, indent_str=_i_)
    code_lines += lambda_code.split("\n")

    pyarg_str = code_utils.indent_code(pyarg_code(function_infos, options),indent_str=options.indent_python_spaces())
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
    code = code + "\n"
    return code


#################################
#           Methods
################################


def _generate_pyi_constructor(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions) -> str:
    return ""

    if "delete" in function_infos.specifiers:
        return ""

    """
    A constructor decl look like this
        .def(py::init<ARG_TYPES_LIST>(),
        PY_ARG_LIST
        DOC_STRING);    
    """

    _i_ = options.indent_python_spaces()

    params_str = function_infos.parameter_list.types_only_for_template()
    doc_string = cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    location = info_cpp_element_original_location(function_infos, options)

    code_lines = []
    code_lines.append(f".def(py::init<{params_str}>(){location}")
    code_lines += pyarg_code_list(function_infos, options)
    if len(doc_string) > 0:
        code_lines.append(f'"{doc_string}"')

    # indent lines after first
    for i in range(1, len(code_lines)):
        code_lines[i] = _i_ + code_lines[i]

    code_lines[-1] = code_utils.add_item_before_comment(code_lines[-1], ")")

    code = code_utils.join_lines_with_token_before_comment(code_lines, ",")
    code += "\n"

    return code


def _generate_pyi_method(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str) -> str:

    return ""

    if function_infos.name == parent_struct_name:
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


def _add_struct_member_decl(cpp_decl: CppDecl, struct_name: str, options: CodeStyleOptions) -> str:

    return ""

    _i_ = options.indent_python_spaces()
    name_cpp = cpp_decl.name_without_array()
    name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    comment = cpp_decl.cpp_element_comments.full_comment()
    location = info_cpp_element_original_location(cpp_decl, options)

    if len(cpp_decl.range) > 0:
        # We ignore bitfields
        return ""

    if cpp_decl.is_c_array_fixed_size():
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options.c_array_numeric_member_types:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Only numeric C Style arrays are supported 
                    Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                options.srcml_options)
            return ""

        if not options.c_array_numeric_member_flag_replace:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Detected a numeric C Style array, but will not export it.
                    Hint: set `options.c_array_numeric_member_flag_replace = True`
                """,
                options.srcml_options)
            return ""

        array_size = cpp_decl.c_array_size()

        if array_size is None:
            array_size_str = cpp_decl.c_array_size_str()
            if array_size_str in options.c_array_numeric_member_size_dict.keys():
                array_size = options.c_array_numeric_member_size_dict[array_size_str]
                if type(array_size) != int:
                    srcml_warnings.emit_srcml_warning(
                        cpp_decl.srcml_element,
                        """
                        options.c_array_numeric_member_size_dict should contains [str,int] items !
                        """,
                        options.srcml_options)
                    return ""
            else:
                srcml_warnings.emit_srcml_warning(
                    cpp_decl.srcml_element,
                    f"""
                    Detected a numeric C Style array, but will not export it because its size is not parsable.
                        Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                    """,
                    options.srcml_options)
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
        code_inner_member  = f'.def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT"){location}\n'
        r = code_inner_member
        r = r.replace("MEMBER_NAME_PYTHON",  name_python)
        r = r.replace("MEMBER_NAME_CPP", name_cpp)
        r = r.replace("MEMBER_COMMENT", cpp_to_python.docstring_python_one_line(comment, options))
        return r


def _add_struct_member_decl_stmt(cpp_decl_stmt: CppDeclStatement, struct_name: str, options: CodeStyleOptions):
    return ""

    r = ""
    for cpp_decl in cpp_decl_stmt.cpp_decls:
        r += _add_struct_member_decl(cpp_decl, struct_name, options)
    return r


def _add_public_struct_elements(public_zone: CppPublicProtectedPrivate, struct_name: str, options: CodeStyleOptions):
    return ""

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
            code = _generate_pyi_method(function_infos = public_child, options=options, parent_struct_name=struct_name)
            r = r + code
        elif isinstance(public_child, CppConstructorDecl):
            code = _generate_pyi_constructor(function_infos = public_child, options=options)
            r = r + code
    return r


def _generate_pyi_struct_or_class(struct_infos: CppStruct, options: CodeStyleOptions) -> str:
    return ""

    struct_name = struct_infos.name

    if struct_infos.template is not None:
        return ""

    _i_ = options.indent_python_spaces()

    comment = cpp_to_python.docstring_python_one_line(struct_infos.cpp_element_comments.full_comment(), options)
    location = info_cpp_element_original_location(struct_infos, options)

    code_intro = ""
    code_intro += f'auto pyClass{struct_name} = py::class_<{struct_name}>{location}\n'
    code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'

    # code_intro += f'{_i_}.def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!

    if options.generate_to_string:
        code_outro = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }});'
    else:
        code_outro = f'{_i_};'

    r = code_intro

    if not struct_infos.has_non_default_ctor() and not struct_infos.has_deleted_default_ctor():
        r += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
    if struct_infos.has_deleted_default_ctor():
        r += f"{_i_}// (default constructor explicitly deleted)\n"

    for child in struct_infos.block.block_children:
        if child.tag() == "public":
            zone_code = _add_public_struct_elements(public_zone=child, struct_name=struct_name, options=options)
            r += code_utils.indent_code(zone_code, indent_str=options.indent_python_spaces())
    r = r + code_outro
    r = r + "\n"
    return r


#################################
#           Namespace
################################
def _generate_pyi_namespace(
        cpp_namespace: CppNamespace,
        options: CodeStyleOptions,
        current_namespaces: List[str] = []) -> str:

    namespace_name = cpp_namespace.name
    new_namespaces = current_namespaces + [namespace_name]
    namespace_code = generate_pyi(cpp_namespace.block, options, new_namespaces)
    location = info_cpp_element_original_location(cpp_namespace, options)

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
        cpp_unit: CppUnit,
        options: CodeStyleOptions,
        current_namespaces: List[str] = [],
        add_boxed_types_definitions: bool = False) -> str:

    r = ""
    for i, cpp_element in enumerate(cpp_unit.block_children):
        if False:
            pass
        elif isinstance(cpp_element, CppFunctionDecl) or isinstance(cpp_element, CppFunction):
            r += _add_one_line_before( _generate_pyi_function(cpp_element, options, parent_struct_name="") )
        elif isinstance(cpp_element, CppEnum):
            r += _add_two_lines_before( _generate_pyi_enum(cpp_element, options) )
        elif isinstance(cpp_element, CppStruct) or isinstance(cpp_element, CppClass):
            r += _add_two_lines_before( _generate_pyi_struct_or_class(cpp_element, options) )
        elif isinstance(cpp_element, CppNamespace):
            r += _add_two_lines_before( _generate_pyi_namespace(cpp_element, options, current_namespaces) )

    if add_boxed_types_definitions:
        pass
        # boxed_structs = cpp_to_python.BoxedImmutablePythonType.struct_codes()
        # boxed_bindings = cpp_to_python.BoxedImmutablePythonType.binding_codes(options)
        # if len(boxed_structs) > 0:
        #     r = boxed_structs + "\n" + boxed_bindings + "\n" + r

    return r
