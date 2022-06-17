import copy
from typing import List, Optional

from litgen.generate_code import LitgenOptions
from litgen.internal.adapt_function import AdaptedFunction
from litgen.internal.adapt_function._lambda_adapter import LambdaAdapter
from srcmlcpp.srcml_types import CppParameter


def is_variadic_format(param: CppParameter):
    return param.decl.cpp_type.typenames == [] and param.decl.cpp_type.modifiers == ["..."]


def adapt_variadic_format(adapted_function: AdaptedFunction, options: LitgenOptions) -> Optional[LambdaAdapter]:
    """A function like
        void Text(const char* fmt, ...)
    will be published in python as
        module.text(s: str)
    and call
        Text("%s", s.c_str());
    """

    old_function_params: List[CppParameter] = adapted_function.function_infos.parameter_list.parameters

    # Variadic params are always last
    if len(old_function_params) < 2:
        return None
    last_param = old_function_params[-1]
    if not is_variadic_format(last_param):
        return None
    param_before_last = old_function_params[-2]
    if not param_before_last.decl.cpp_type.str_code() == "const char *":
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.function_infos)
    new_function_params = []

    # process all params except last
    for old_param in old_function_params[:-2]:
        new_function_params.append(old_param)
        lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)
    # Process param_before_last (const char *)
    new_function_params.append(param_before_last)
    lambda_adapter.adapted_cpp_parameter_list.append('"%s"')
    # Process last_param
    lambda_adapter.adapted_cpp_parameter_list.append(param_before_last.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params
    lambda_adapter.lambda_name = adapted_function.function_infos.function_name + "_adapt_variadic_format"

    return lambda_adapter
