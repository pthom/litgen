from code_types import *
import code_types
from options import CodeStyleOptions
from function_wrapper_lambda import \
    make_function_wrapper_lambda, make_method_wrapper_lambda, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format
import code_utils
import cpp_to_python


def generate_python_wrapper_init_code(function_infos: FunctionsInfos, options: CodeStyleOptions) -> str:
    """
    Should generate code like this:

    def image_display(
        np.ndarray image,
        Size image_display_size = (0, 0),
        refresh_image = False
        ):
        '''Only, display the image, with no decoration, and no user interaction
        '''
        _cpp_immvision.image_display(image, image_display_size, refresh_image)
    """
    py_function_name = cpp_to_python.function_name_to_python(function_infos.function_name_cpp(), options)
    title = code_utils.indent_code(cpp_to_python.docstring_python(function_infos.function_code.docstring_cpp, options), 4)[4:]

    code_intro = f'def {py_function_name}(\n'
    param_line_template  = f'PARAM_NAME: PARAM_TYPE PARAM_DEFAULT'
    code_outro = f'):\n    """{title}\n    """\n'

    r = code_intro
    param_lines = []
    for param in function_infos.get_parameters():
        param_line = param_line_template
        param_line = param_line.replace("PARAM_TYPE", cpp_to_python.type_to_python(param.type_cpp, options))
        param_line = param_line.replace("PARAM_NAME", cpp_to_python.var_name_to_python(param.name_cpp, options))
        if len(param.default_value_cpp) > 0:
            param_line = param_line.replace(
                "PARAM_DEFAULT",
                " = " + cpp_to_python.default_value_to_python(param.default_value_cpp, options))
        else:
            param_line = param_line.replace(" PARAM_DEFAULT", "")
        param_lines.append(param_line.strip())
    params_str = ",\n".join(param_lines)
    params_str = code_utils.indent_code(params_str, 4)
    r = r + params_str

    # If no parameters, make sure that we have a definition of the form:
    #       def clear_texture_cache():
    # instead of
    #       def clear_texture_cache(
    #       ):
    #
    if len(function_infos.parameters) == 0:
        r = r[:-1]

    r = r + code_outro

    if options.init_function_python_additional_code is not None:
        r += options.init_function_python_additional_code(function_infos)
    r = r + f"    r = {options.package_name_native}.{py_function_name}("

    r += cpp_to_python.params_names_to_python(function_infos.get_parameters(), options)

    r = r + ")\n"
    r = r + '    return r\n'

    r = r + "\n\n"
    return r






def generate_constructor_code(
        function_infos: FunctionsInfos,
        options: CodeStyleOptions) -> str:

    def pydef_attributes_as_cpp_types_only(attrs: List[PydefAttribute]) -> str:
        strs = map(lambda attr: attr.type_cpp, attrs)
        return ", ".join(strs)

    # Default constructors are always generated!
    if len(function_infos.get_parameters()) == 0:
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
    params_str = pydef_attributes_as_cpp_types_only(function_infos.get_parameters())

    code = code.replace("PARAMS", params_str)
    code = code.replace("PYARGS", pyarg_str)
    code = code.replace("CONSTRUCTOR_DOC",
                        cpp_to_python.docstring_python_one_line(function_infos.function_code.docstring_cpp, options))

    code = code_utils.unindent_code(code)
    code = code_utils.indent_code(code, 4)
    return code


def generate_pydef_method_cpp_code(
        function_infos: FunctionsInfos,
        options: CodeStyleOptions,
        parent_struct_name: str) -> str:

    if function_infos.function_name_cpp() == parent_struct_name:
        return generate_constructor_code(function_infos, options)
    if function_infos.function_name_cpp() == "~" + parent_struct_name:
        return ""
    return generate_pydef_function_cpp_code(function_infos, options, parent_struct_name)
