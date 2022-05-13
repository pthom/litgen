from code_types import *
from options import CodeStyleOptions
from function_wrapper_lambda import \
    make_function_wrapper_lambda, make_method_wrapper_lambda, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format
import code_utils


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
    py_function_name = function_infos.function_name_python(options)
    title = code_utils.indent_code(function_infos.function_code.title_python(options), 4)[4:]

    code_intro = f'def {py_function_name}(\n'
    param_line_template  = f'PARAM_NAME: PARAM_TYPE PARAM_DEFAULT'
    code_outro = f'):\n    """{title}\n    """\n'

    r = code_intro
    param_lines = []
    for param in function_infos.get_parameters():
        param_line = param_line_template
        param_line = param_line.replace("PARAM_TYPE", param.type_python(options))
        param_line = param_line.replace("PARAM_NAME", param.name_python())
        if len(param.default_value_cpp) > 0:
            param_line = param_line.replace(
                "PARAM_DEFAULT",
                " = " + param.default_value_python(options))
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
    params_list = []
    for param in function_infos.get_parameters():
        params_list.append(param.name_python())
    r = r + ", ".join(params_list)

    r = r + ")\n"
    r = r + '    return r\n'

    r = r + "\n\n"
    return r


def add_pyarg_lines(function_infos: FunctionsInfos, options: CodeStyleOptions) -> List[str]:
    param_lines = []
    code_inner_defaultvalue = '    py::arg("ARG_NAME_PYTHON") = ARG_DEFAULT_VALUE'
    code_inner_nodefaultvalue = '    py::arg("ARG_NAME_PYTHON")'

    for idx_param, param in enumerate(function_infos.get_parameters()):
        if len(param.default_value_cpp) > 0:
            if is_default_sizeof_param(param, options):
                default_value_cpp = "-1"
            else:
                default_value_cpp = param.default_value_cpp
            param_line = code_inner_defaultvalue \
                .replace("ARG_NAME_PYTHON", param.name_python()) \
                .replace("ARG_DEFAULT_VALUE", default_value_cpp)
        else:
            if is_buffer_size_name_at_idx(function_infos.get_parameters(), options, idx_param):
                continue
            if  is_param_variadic_format(function_infos.parameters, options, idx_param):
                continue
            param_line= code_inner_nodefaultvalue.replace("ARG_NAME_PYTHON", param.name_python())

        param_line += ","
        param_lines.append(param_line)

    return param_lines


def generate_pydef_function_cpp_code(
        function_infos: FunctionsInfos,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
        ) -> str:

    is_method = len(parent_struct_name) > 0

    fn_name_python = function_infos.function_name_python(options)

    code_intro = f'.def("{fn_name_python}",'
    if not is_method:
        code_intro = "m" + code_intro

    code_lines = [""]
    code_lines += [code_intro]
    lambda_code = make_function_wrapper_lambda(function_infos, options, parent_struct_name)
    lambda_code = code_utils.indent_code(lambda_code, 4)
    code_lines += lambda_code.split("\n")
    code_lines += add_pyarg_lines(function_infos, options)

    comment_cpp = code_utils.format_cpp_comment_on_one_line(function_infos.function_code.title_python(options))
    code_lines += [f'    "{comment_cpp}"']
    if is_method:
        code_lines += ")"
    else:
        code_lines += [');']
    code_lines += ["", ""]

    code = "\n".join(code_lines)
    code = code_utils.indent_code(code, options.indent_size_functions_pydef)
    return code


def generate_pydef_method_cpp_code(
        function_infos: FunctionsInfos,
        options: CodeStyleOptions,
        parent_struct_name: str) -> str:

    return generate_pydef_function_cpp_code(function_infos, options, parent_struct_name)
