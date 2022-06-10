from dataclasses import dataclass

from litgen.options import CodeStyleOptions
from litgen.internal.cpp_function_adapted_params import CppFunctionDeclWithAdaptedParams

from srcmlcpp.srcml_types import CppFunctionDecl


def make_function_params_adapter(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> CppFunctionDeclWithAdaptedParams:

    from litgen.internal.function_adapt_c_arrays import adapt_c_arrays

    function_adapted_params = CppFunctionDeclWithAdaptedParams(function_infos)
    adapt_c_arrays(function_adapted_params, options, parent_struct_name)
    return function_adapted_params
