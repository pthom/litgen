from typing import Optional
import copy
import enum
from dataclasses import dataclass

from litgen.generate_code import CodeStyleOptions, generate_pydef
from litgen.internal import cpp_to_python
from litgen.internal.function_params_adapter import CppFunctionDeclWithAdaptedParams

from srcmlcpp.srcml_types import CppFunctionDecl, CppParameter, CppParameterList, CppType, CppDecl


def adapt_c_arrays(function_adapted_params: CppFunctionDeclWithAdaptedParams,
                   options: CodeStyleOptions,
                   parent_struct_name: str = ""
                   ) -> CppFunctionDeclWithAdaptedParams:
    """
    We want to adapt functions that use fixed size C arrays like this one:
        void truc(int v[2])
        {
            v[0] += 1;
            v[1] += 2;
        }

    With an additional lambda that will look like:
        auto truc_v_cpp_array = [](std::array<BoxedInt, 4>& v)
        {
            truc(v.data());
        };
    """
    needs_adapt = False
    for param in function_adapted_params.function_infos.parameter_list.parameters:
        if param.decl.is_c_array_fixed_size():
            needs_adapt = True

    if not needs_adapt:
        return

    adapted_cpp_parameter_list = []
    new_function_infos = copy.deepcopy(function_adapted_params.function_infos)
    for param in new_function_infos.parameter_list.parameters:
        if param.decl.is_c_array_fixed_size():
            param.decl = param.decl.c_array_fixed_size_to_std_array()
            adapted_cpp_parameter_list.append(param.decl.name + ".data()")
        else:
            adapted_cpp_parameter_list.append(param.decl.name)

    lambda_name = function_adapted_params.function_infos.name + "_adapt_fixed_size_c_arrays"
    capture_this = "this" if len(parent_struct_name) > 0 else ""
    adapted_python_parameter_list_str = new_function_infos.parameter_list.str_code()
    adapted_cpp_parameter_list_str = ", ".join(adapted_cpp_parameter_list)

    _i_ = options.indent_cpp_spaces()
    lambda_code = ""
    lambda_code += f"auto {lambda_name} = [{capture_this}]({adapted_python_parameter_list_str})\n"
    lambda_code += "{\n"
    lambda_code += f"{_i_}return {function_adapted_params.function_infos.name}({adapted_cpp_parameter_list_str});\n"
    lambda_code += "};\n"

    function_adapted_params.cpp_adapter_code += lambda_code
    function_adapted_params.function_infos = new_function_infos
    function_adapted_params.lambda_to_call = lambda_name
