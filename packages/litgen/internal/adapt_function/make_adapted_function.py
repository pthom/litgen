from codemanip import code_utils
from litgen.internal.adapt_function import AdaptedFunction
from litgen.internal.adapt_function._lambda_adapter import LambdaAdapter
from litgen.options import LitgenOptions
from srcmlcpp.srcml_types import CppFunctionDecl


def apply_all_adapters(inout_adapted_function: AdaptedFunction) -> None:
    from litgen.internal.adapt_function._adapt_c_arrays import adapt_c_arrays
    from litgen.internal.adapt_function._adapt_c_string_list import adapt_c_string_list
    from litgen.internal.adapt_function._adapt_c_buffers import adapt_c_buffers
    from litgen.internal.adapt_function._adapt_variadic_format import adapt_variadic_format

    all_adapters_functions = [
        adapt_c_buffers,
        adapt_c_arrays,
        adapt_c_string_list,
        adapt_variadic_format,
    ]
    for adapter_function in all_adapters_functions:
        lambda_adapter = adapter_function(inout_adapted_function)
        if lambda_adapter is not None:
            _apply_lambda_adapter(inout_adapted_function, lambda_adapter)


def make_adapted_function_with_cpp_adapter_code(
    function_infos: CppFunctionDecl,
    options: LitgenOptions,
    parent_struct_name: str = "",
) -> AdaptedFunction:

    adapted_function = AdaptedFunction(function_infos, parent_struct_name, options)
    apply_all_adapters(adapted_function)
    return adapted_function


def _make_adapted_lambda_code_end(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter):
    options = adapted_function.options
    lambda_template_code = """
        {auto_r_equal_or_void}{function_or_lambda_to_call}({adapted_cpp_parameters});
        {maybe_lambda_output_code}
        {maybe_return_r};
    """
    lambda_template_code = code_utils.unindent_code(lambda_template_code, flag_strip_empty_lines=True)

    # Fill _i_
    _i_ = options.indent_cpp_spaces()

    # Fill adapted_cpp_parameters
    adapted_cpp_parameters = ", ".join(lambda_adapter.adapted_cpp_parameter_list)

    # Fill auto_r_equal_or_void
    _fn_return_type = adapted_function.function_infos.full_return_type(options.srcml_options)
    auto_r_equal_or_void = "auto r = " if _fn_return_type != "void" else ""

    # Fill function_or_lambda_to_call
    if adapted_function.lambda_to_call is not None:
        function_or_lambda_to_call = adapted_function.lambda_to_call
    else:
        if adapted_function.is_method():
            function_or_lambda_to_call = "self." + adapted_function.function_infos.function_name
        else:
            function_or_lambda_to_call = adapted_function.function_infos.function_name

    # Fill maybe_return_r
    maybe_return_r = None if _fn_return_type == "void" else "return r"

    # Fill maybe_lambda_output_code
    if len(lambda_adapter.lambda_output_code) > 0:
        maybe_lambda_output_code = "\n" + code_utils.strip_empty_lines(lambda_adapter.lambda_output_code)
    else:
        maybe_lambda_output_code = None

    #
    # Apply replacements
    #
    lambda_code = lambda_template_code
    lambda_code = code_utils.replace_in_string_remove_line_if_none(
        lambda_code,
        {
            "maybe_return_r": maybe_return_r,
            "maybe_lambda_output_code": maybe_lambda_output_code,
        },
    )
    lambda_code = code_utils.replace_in_string(
        lambda_code,
        {
            "_i_": _i_,
            "auto_r_equal_or_void": auto_r_equal_or_void,
            "function_or_lambda_to_call": function_or_lambda_to_call,
            "adapted_cpp_parameters": adapted_cpp_parameters,
        },
    )

    return lambda_code


def _make_adapted_lambda_code(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter):
    lambda_template_code = """
        auto {lambda_name} = [{lambda_captures}]({adapted_python_parameters})
        {
        {_i_}{maybe_lambda_input_code}
        {_i_}{lambda_template_end}
        };
    """
    options = adapted_function.options
    lambda_template_code = code_utils.unindent_code(lambda_template_code, flag_strip_empty_lines=True) + "\n"

    # Fill _i_
    _i_ = options.indent_cpp_spaces()

    # Fill lambda_name
    lambda_name = lambda_adapter.lambda_name

    # Fill lambda_captures
    _lambda_captures_list = []
    if adapted_function.lambda_to_call is not None:
        _lambda_captures_list.append("&" + adapted_function.lambda_to_call)
    elif adapted_function.is_method():
        _lambda_captures_list.append("&self")
    lambda_captures = ", ".join(_lambda_captures_list)

    # Fill adapted_python_parameters
    assert lambda_adapter.new_function_infos is not None
    adapted_python_parameters = lambda_adapter.new_function_infos.parameter_list.str_code()

    # Fill maybe_lambda_input_code
    if len(lambda_adapter.lambda_input_code) > 0:
        maybe_lambda_input_code = code_utils.indent_code(
            lambda_adapter.lambda_input_code,
            indent_str=options.indent_cpp_spaces(),
            skip_first_line=True,
        )
    else:
        maybe_lambda_input_code = None

    # Fill lambda_template_end
    if lambda_adapter.lambda_template_end is not None:
        lambda_template_end = lambda_adapter.lambda_template_end
    else:
        lambda_template_end = _make_adapted_lambda_code_end(adapted_function, lambda_adapter)
    lambda_template_end = code_utils.indent_code(
        lambda_template_end,
        indent_str=options.indent_cpp_spaces(),
        skip_first_line=True,
    )

    #
    # Apply replacements
    #
    lambda_code = lambda_template_code
    lambda_code = code_utils.replace_in_string_remove_line_if_none(
        lambda_code, {"maybe_lambda_input_code": maybe_lambda_input_code}
    )
    lambda_code = code_utils.replace_in_string(
        lambda_code,
        {
            "_i_": _i_,
            "lambda_name": lambda_name,
            "lambda_captures": lambda_captures,
            "adapted_python_parameters": adapted_python_parameters,
            "lambda_template_end": lambda_template_end,
        },
    )

    return lambda_code


def _apply_lambda_adapter(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter):
    options = adapted_function.options

    # Get the full lambda code
    lambda_code = _make_adapted_lambda_code(adapted_function, lambda_adapter)

    # And modify adapted_function
    if adapted_function.cpp_adapter_code is None:
        adapted_function.cpp_adapter_code = lambda_code
    else:
        adapted_function.cpp_adapter_code += lambda_code

    assert lambda_adapter.new_function_infos is not None
    adapted_function.function_infos = lambda_adapter.new_function_infos
    adapted_function.lambda_to_call = lambda_adapter.lambda_name
