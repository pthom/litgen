from dataclasses import dataclass

from litgen.options import CodeStyleOptions
from litgen.internal.cpp_function_adapted_params import CppFunctionDeclWithAdaptedParams, LambdaAdapter
from litgen.internal import code_utils

from srcmlcpp.srcml_types import CppFunctionDecl


def make_function_params_adapter(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> CppFunctionDeclWithAdaptedParams:

    from litgen.internal.function_adapt_c_arrays import adapt_c_arrays
    from litgen.internal.function_adapt_c_string_list import adapt_c_string_list
    all_adapters_functions = [adapt_c_arrays, adapt_c_string_list]

    function_adapted_params = CppFunctionDeclWithAdaptedParams(function_infos)

    for adapter_function in all_adapters_functions:
        lambda_adapter = adapter_function(function_adapted_params, options)
        if lambda_adapter is not None:
            apply_lambda_adapter(function_adapted_params, lambda_adapter, options, parent_struct_name)

    return function_adapted_params


def apply_lambda_adapter(
        function_adapted_params: CppFunctionDeclWithAdaptedParams,
        lambda_adapter: LambdaAdapter,
        options: CodeStyleOptions,
        parent_struct_name):

    _i_ = options.indent_cpp_spaces()

    lambda_captures_list = []

    is_method = len(parent_struct_name) > 0
    if function_adapted_params.lambda_to_call is not None:
        lambda_captures_list.append("&" + function_adapted_params.lambda_to_call)
    elif is_method:
        lambda_captures_list.append("&self")

    lambda_captures_str = ", ".join(lambda_captures_list)

    adapted_python_parameter_list_str = lambda_adapter.new_function_infos.parameter_list.str_code()
    adapted_cpp_parameter_list_str = ", ".join(lambda_adapter.adapted_cpp_parameter_list)

    lambda_code = ""
    lambda_code += f"auto {lambda_adapter.lambda_name} = [{lambda_captures_str}]({adapted_python_parameter_list_str})\n"
    lambda_code += "{\n"
    fn_return_type = function_adapted_params.function_infos.full_return_type(options.srcml_options)

    capture_return_code = "" if fn_return_type == "void" else "auto r = "

    # Which function to call: either the last lambda, or the original function, or the original method
    if function_adapted_params.lambda_to_call is not None:
        function_or_lambda_to_call = function_adapted_params.lambda_to_call
    else:
        if is_method:
            function_or_lambda_to_call = "self." + function_adapted_params.function_infos.name
        else:
            function_or_lambda_to_call = function_adapted_params.function_infos.name

    if len(lambda_adapter.lambda_input_code) > 0:
        lambda_code += code_utils.indent_code(lambda_adapter.lambda_input_code, indent_str=options.indent_cpp_spaces()) + "\n"
    lambda_code += f"{_i_}{capture_return_code}{function_or_lambda_to_call}({adapted_cpp_parameter_list_str});\n"
    if len(lambda_adapter.lambda_output_code) > 0:
        lambda_code += "\n" + code_utils.indent_code(lambda_adapter.lambda_output_code, indent_str=options.indent_cpp_spaces())
    if len(capture_return_code) > 0:
        if len(lambda_adapter.lambda_output_code) > 0:
            lambda_code += "\n"
        lambda_code += f"{_i_}return r;\n"
    lambda_code += "};\n"

    if function_adapted_params.cpp_adapter_code is None:
        function_adapted_params.cpp_adapter_code = lambda_code
    else:
        function_adapted_params.cpp_adapter_code += lambda_code
    function_adapted_params.function_infos = lambda_adapter.new_function_infos
    function_adapted_params.lambda_to_call = lambda_adapter.lambda_name
