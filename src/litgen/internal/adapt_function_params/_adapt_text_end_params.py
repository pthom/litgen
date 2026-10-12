from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction


def adapt_text_end_params(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    """
    We want to remove the "text end" params from functions signatures, based on options.fn_params_text_end_names__regex:
        void SeparatorTextEx(const char* label, const char* label_end, float extra_width);
    is published as
        def separator_text_ex(label: str, extra_width: float) -> None
    and calls SeparatorTextEx(label, label + strlen(label), extra_width).
    A text end param with a default value receives its default value instead.
    """
    options = adapted_function.options

    old_function_params: list[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters

    def is_const_char_pointer(param: CppParameter) -> bool:
        return param.decl.cpp_type.str_code() == "const char *"

    def is_text_end(idx: int) -> bool:
        param = old_function_params[idx]
        return (
            idx > 0
            and is_const_char_pointer(param)
            and is_const_char_pointer(old_function_params[idx - 1])
            and code_utils.does_match_regex_or_matcher(options.fn_params_text_end_names__regex, param.decl.decl_name)
        )

    if not any(is_text_end(idx) for idx in range(len(old_function_params))):
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)
    new_function_params = []

    for idx, old_param in enumerate(old_function_params):
        if is_text_end(idx):
            if old_param.has_default_value():
                lambda_adapter.adapted_cpp_parameter_list.append(old_param.default_value())
            else:
                text = old_function_params[idx - 1].decl.decl_name
                lambda_adapter.adapted_cpp_parameter_list.append(f"{text} ? {text} + strlen({text}) : nullptr")
        else:
            new_function_params.append(old_param)
            lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_text_end_params"

    return lambda_adapter
