from __future__ import annotations
import copy

from srcmlcpp.cpp_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction


def adapt_force_lambda(adapted_function: AdaptedFunction) -> LambdaAdapter:
    """
    This adapter simply forces the usage of a lambda. Can be sometimes useful when pybind11 is confused
    and gives error like
        error: no matching function for call to object of type 'const detail::overload_cast_impl<...>'
    """
    old_function_params: list[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)
    new_function_params = []
    for old_param in old_function_params:
        new_function_params.append(old_param)
        lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params
    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_force_lambda"

    return lambda_adapter
