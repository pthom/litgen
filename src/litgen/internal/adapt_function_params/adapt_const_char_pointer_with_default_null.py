import copy

from typing import Optional
from codemanip import code_utils
from srcmlcpp.cpp_types import CppParameter
from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction, AdaptedParameter


def adapt_const_char_pointer_with_default_null(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    options = adapted_function.options

    if not options.fn_params_const_char_pointer_with_default_null:
        return None

    function_name = adapted_function.cpp_adapted_function.function_name
    if not code_utils.does_match_regex(options.fn_params_output_modifiable_immutable_to_return__regex, function_name):
        return None

    needs_adapt = False

    for old_adapted_param in adapted_function.adapted_parameters():
        if old_adapted_param.is_const_char_pointer_with_default_null():
            needs_adapt = True

    if not needs_adapt:
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)

    old_function_params: list[AdaptedParameter] = adapted_function.adapted_parameters()

    new_function_params: list[CppParameter] = []
    for old_adapted_param in old_function_params:
        if old_adapted_param.is_const_char_pointer_with_default_null():
            new_param = copy.deepcopy(old_adapted_param.cpp_element())
            new_decl = new_param.decl
            new_decl.cpp_type.modifiers = []
            new_decl.cpp_type.specifiers = []
            new_decl.cpp_type.typenames = ["std::optional<std::string>"]
            new_decl.initial_value_code = "std::nullopt"

            new_function_params.append(new_param)

            param_original_type = old_adapted_param.cpp_element().full_type()
            param_name_value = old_adapted_param.cpp_element().decl.decl_name + "_adapt_default_null"
            param_name = old_adapted_param.cpp_element().decl.decl_name
            _i_ = options._indent_cpp_spaces()

            lambda_input_code = f"""
                {param_original_type} {param_name_value} = nullptr;
                if ({param_name}.has_value())
                {_i_}{param_name_value} = {param_name}.value().c_str();
            """

            lambda_adapter.lambda_input_code += (
                code_utils.unindent_code(lambda_input_code, flag_strip_empty_lines=True) + "\n"
            )

            #
            # Fill adapted_cpp_parameter_list (those that will call the original C style function)
            #
            lambda_adapter.adapted_cpp_parameter_list.append(f"{param_name_value}")

        else:
            new_function_params.append(old_adapted_param.cpp_element())
            lambda_adapter.adapted_cpp_parameter_list.append(old_adapted_param.cpp_element().decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params
    lambda_adapter.lambda_name = (
        adapted_function.cpp_adapted_function.function_name + "_adapt_const_char_pointer_with_default_null"
    )

    return lambda_adapter
