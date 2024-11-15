from __future__ import annotations
from munch import Munch  # type: ignore

from codemanip import code_utils
from litgen import BindLibraryType

from srcmlcpp.cpp_types import CppFunctionDecl
from srcmlcpp import srcmlcpp_main

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction


def apply_all_adapters(inout_adapted_function: AdaptedFunction) -> None:
    from litgen.internal.adapt_function_params._adapt_exclude_params import adapt_exclude_params
    from litgen.internal.adapt_function_params._adapt_c_arrays import adapt_c_arrays
    from litgen.internal.adapt_function_params._adapt_c_string_list import (
        adapt_c_string_list,
        adapt_c_string_list_no_count,
    )
    from litgen.internal.adapt_function_params._adapt_c_buffers import adapt_c_buffers
    from litgen.internal.adapt_function_params._adapt_variadic_format import adapt_variadic_format
    from litgen.internal.adapt_function_params.adapt_modifiable_immutable import adapt_modifiable_immutable
    from litgen.internal.adapt_function_params._adapt_force_lambda import adapt_force_lambda
    from litgen.internal.adapt_function_params.adapt_modifiable_immutable_to_return import (
        adapt_modifiable_immutable_to_return,
    )
    from litgen.internal.adapt_function_params.adapt_const_char_pointer_with_default_null import (
        adapt_const_char_pointer_with_default_null,
    )
    from litgen.internal.adapt_function_params._adapt_mutable_param_with_default_value import (
        adapt_mutable_param_with_default_value,
    )

    is_constructor = inout_adapted_function.cpp_adapted_function.is_constructor()
    if is_constructor:
        _apply_all_adapters_on_constructor(inout_adapted_function)
        return

    # Logic test: we should have parents
    def assert_parents_are_present() -> None:
        original_function: CppFunctionDecl = inout_adapted_function.cpp_element()
        adapted_function: CppFunctionDecl = inout_adapted_function.cpp_adapted_function
        if len(original_function.parameter_list.parameters) > 0:
            assert original_function.parameter_list.parameters[0].parent is not None
        if len(adapted_function.parameter_list.parameters) > 0:
            assert adapted_function.parameter_list.parameters[0].parent is not None

    assert_parents_are_present()

    all_adapters_functions = [
        adapt_c_buffers, # must be done at start
        adapt_exclude_params,
        adapt_mutable_param_with_default_value,  # must be done just after adapt_exclude_params
        adapt_c_arrays,
        adapt_const_char_pointer_with_default_null,
        adapt_modifiable_immutable_to_return,
        adapt_modifiable_immutable,  # must be done *after* adapt_c_buffers
        adapt_c_string_list,
        adapt_c_string_list_no_count,
        adapt_variadic_format,
    ]
    all_adapters_functions += inout_adapted_function.options.fn_custom_adapters

    for adapter_function in all_adapters_functions:
        lambda_adapter = adapter_function(inout_adapted_function)
        if lambda_adapter is not None:
            _apply_lambda_adapter(inout_adapted_function, lambda_adapter)

    flag_force_lambda = code_utils.does_match_regex(
        inout_adapted_function.options.fn_force_lambda__regex, inout_adapted_function.cpp_adapted_function.function_name
    )
    if flag_force_lambda and inout_adapted_function.lambda_to_call is None:
        lambda_adapter = adapt_force_lambda(inout_adapted_function)
        _apply_lambda_adapter(inout_adapted_function, lambda_adapter)


def _apply_all_adapters_on_constructor(inout_adapted_function: AdaptedFunction) -> None:
    parent_struct = inout_adapted_function.cpp_element().parent_struct_if_method()
    assert parent_struct is not None

    parameter_list = inout_adapted_function.cpp_element().parameter_list

    if inout_adapted_function.options.bind_library == BindLibraryType.pybind11:
        ctor_wrapper_signature_template = code_utils.unindent_code(
            """
                std::unique_ptr<{class_name}> ctor_wrapper({parameters_code});
            """,
            flag_strip_empty_lines=True,
        )
        ctor_wrapper_lambda_template = code_utils.unindent_code(
            """
                auto ctor_wrapper = []({parameters_code}) ->  std::unique_ptr<{class_name}>
                {
                    return std::make_unique<{class_name}>({parameters_names});
                };
            """,
            flag_strip_empty_lines=True,
        )
    else:
        ctor_wrapper_signature_template = code_utils.unindent_code(
            """
                void ctor_wrapper({class_name}* self, {parameters_code});
            """,
            flag_strip_empty_lines=True,
        )
        ctor_wrapper_lambda_template = code_utils.unindent_code(
            """
                auto ctor_wrapper = []({class_name}* self, {parameters_code}) ->  void
                {
                    new(self) {class_name}({parameters_names}); // placement new
                };
            """,
            flag_strip_empty_lines=True,
        )

    replacements = Munch()
    replacements.parameters_code = parameter_list.str_types_names_default_for_signature()
    replacements.class_name = parent_struct.qualified_class_name_with_specialization()
    replacements.parameters_names = parameter_list.str_names_only_for_call()

    ctor_wrapper_signature_code = code_utils.process_code_template(ctor_wrapper_signature_template, replacements)
    ctor_wrapper_lambda_code = code_utils.process_code_template(ctor_wrapper_lambda_template, replacements)

    cpp_wrapper_function = srcmlcpp_main.code_first_function_decl(
        inout_adapted_function.options.srcmlcpp_options, ctor_wrapper_signature_code
    )
    cpp_wrapper_function.cpp_element_comments.comment_on_previous_lines = inout_adapted_function.cpp_element().cpp_element_comments.comment_on_previous_lines
    cpp_wrapper_function.parent = inout_adapted_function.cpp_element().parent
    ctor_adapted_wrapper_function = AdaptedFunction(
        inout_adapted_function.lg_context,
        cpp_wrapper_function,
        is_overloaded=False,
        initial_lambda_to_call="ctor_wrapper",
    )
    inout_adapted_function.cpp_element().cpp_element_comments.comment_on_previous_lines = cpp_wrapper_function.cpp_element_comments.comment_on_previous_lines

    if ctor_adapted_wrapper_function.cpp_adapter_code is not None:
        inout_adapted_function.cpp_adapter_code = (
            ctor_wrapper_lambda_code + "\n" + ctor_adapted_wrapper_function.cpp_adapter_code
        )
        inout_adapted_function.lambda_to_call = ctor_adapted_wrapper_function.lambda_to_call

    inout_adapted_function.cpp_adapted_function = ctor_adapted_wrapper_function.cpp_adapted_function


def _make_adapted_lambda_code_end(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter) -> str:
    options = adapted_function.options
    lambda_template_code = """
        {auto_r_equal_or_void}{function_or_lambda_to_call}({adapted_cpp_parameters});
        {maybe_lambda_output_code}
        {maybe_return_r};
    """
    lambda_template_code = code_utils.unindent_code(lambda_template_code, flag_strip_empty_lines=True)

    # Fill _i_
    _i_ = options._indent_cpp_spaces()

    # Fill adapted_cpp_parameters
    adapted_cpp_parameters = ", ".join(lambda_adapter.adapted_cpp_parameter_list)

    # Fill auto_r_equal_or_void
    _fn_return_type = adapted_function.cpp_adapted_function.str_full_return_type()
    auto_r_equal_or_void = "auto lambda_result = " if _fn_return_type != "void" else ""

    # Fill function_or_lambda_to_call
    if adapted_function.lambda_to_call is not None:
        function_or_lambda_to_call = adapted_function.lambda_to_call
    else:
        if adapted_function.is_method():
            function_or_lambda_to_call = (
                "self." + adapted_function.cpp_adapted_function.function_name_with_specialization()
            )
        else:
            function_or_lambda_to_call = (
                adapted_function.cpp_adapted_function.qualified_function_name_with_specialization()
            )

    # Fill maybe_return_r
    maybe_return_r = None if _fn_return_type == "void" else "return lambda_result"

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


def _make_adapted_lambda_code(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter) -> str:
    lambda_template_code = """
        auto {lambda_name} = [{lambda_captures}]({adapted_python_parameters}){lambda_return_arrow}
        {
        {_i_}{maybe_lambda_input_code}
        {_i_}{lambda_template_end}
        };
    """
    options = adapted_function.options
    lambda_template_code = code_utils.unindent_code(lambda_template_code, flag_strip_empty_lines=True) + "\n"

    # Fill _i_
    _i_ = options._indent_cpp_spaces()

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

    # Fill lambda_return_arrow
    # full_return_type = adapted_function.cpp_adapted_function.full_return_type(options.srcmlcpp_options)
    full_return_type = lambda_adapter.new_function_infos.str_full_return_type()
    if full_return_type == "void":
        lambda_return_arrow = ""
    else:
        lambda_return_arrow = f" -> {full_return_type}"

    # Fill maybe_lambda_input_code
    if len(lambda_adapter.lambda_input_code) > 0:
        maybe_lambda_input_code = code_utils.indent_code(
            lambda_adapter.lambda_input_code,
            indent_str=options._indent_cpp_spaces(),
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
        indent_str=options._indent_cpp_spaces(),
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
            "lambda_return_arrow": lambda_return_arrow,
            "adapted_python_parameters": adapted_python_parameters,
            "lambda_template_end": lambda_template_end,
        },
    )

    return lambda_code


def _apply_lambda_adapter(adapted_function: AdaptedFunction, lambda_adapter: LambdaAdapter) -> None:
    # Get the full lambda code
    lambda_code = _make_adapted_lambda_code(adapted_function, lambda_adapter)

    # And modify adapted_function
    if adapted_function.cpp_adapter_code is None:
        adapted_function.cpp_adapter_code = lambda_code
    else:
        adapted_function.cpp_adapter_code += lambda_code

    assert lambda_adapter.new_function_infos is not None
    adapted_function.cpp_adapted_function = lambda_adapter.new_function_infos
    adapted_function.lambda_to_call = lambda_adapter.lambda_name
