from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction


def adapt_exclude_params(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    """
    We want to remove params from functions signatures, based on options.fn_params_exclude_regexes
    """
    options = adapted_function.options

    old_function_params: list[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters

    def shall_exclude(param: CppParameter) -> bool:
        param_name = param.decl.decl_name
        matches_regex_name = code_utils.does_match_regex(options.fn_params_exclude_names__regex, param_name)
        param_cpp_type = param.decl.cpp_type.str_code()
        matches_regex_type = code_utils.does_match_regex(options.fn_params_exclude_types__regex, param_cpp_type)
        has_default_value = param.has_default_value()
        r = (matches_regex_name or matches_regex_type) and has_default_value
        return r

    def needs_adapt() -> bool:
        for param in old_function_params:
            if shall_exclude(param):
                return True
        return False

    if not needs_adapt():
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)
    new_function_params = []

    for old_param in old_function_params:
        if shall_exclude(old_param):
            #
            # Create new calling param (std::vector<std::string> &) -> not needed
            #

            #
            # Fill lambda_input_code -> not needed
            #

            #
            # Fill adapted_cpp_parameter_list (those that will call the original C style function)
            #
            lambda_adapter.adapted_cpp_parameter_list.append(old_param.default_value())

        else:
            new_function_params.append(old_param)
            lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_exclude_params"

    return lambda_adapter
