from typing import Optional
import copy
import enum
from dataclasses import dataclass

from litgen.generate_code import CodeStyleOptions, generate_pydef
from litgen.internal import cpp_to_python

from srcmlcpp.srcml_types import CppFunctionDecl, CppParameter, CppParameterList, CppType, CppDecl


@dataclass
class CppFunctionDeclWithAdaptedParams:
    function_infos: CppFunctionDecl
    cpp_adapter_code: str
    lambda_to_call: str

    def __init__(self, function_infos: CppFunctionDecl):
        self.function_infos = function_infos
        self.cpp_adapter_code = ""
        self.lambda_to_call = self.function_infos.name


def _boxed_number_cpp_struct(number_type: str) -> str:
    if number_type not in number_type in cpp_to_python.cpp_numeric_types():
        raise ValueError(f"""
        type {number_type} is not supported as a number type. Here is the supported list:
            {cpp_to_python.cpp_numeric_types()}""")

    struct_code = f"""struct Boxed{number_type}
{{
    {number_type} value;
    std::string __repr__() {{ return std::string("Boxed{number_type}(") + std::to_string(value) + ")"; }}
}};"""
    return struct_code


def _boxed_number_cpp_binding(number_type: str, options: CodeStyleOptions) -> str:
    struct_code = _boxed_number_cpp_struct(number_type)
    pydef_code = generate_pydef(struct_code, options)
    return pydef_code


def _adapt_fixed_size_c_arrays(function_adapted_params: CppFunctionDeclWithAdaptedParams,
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
            truc(v.data()); // .mutable_data() if v not const
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
            param.decl = param.decl.c_array_fixed_size_to_py_array()
            if param.decl.is_const():
                adapted_cpp_parameter_list.append(param.decl.name + ".data()")
            else:
                adapted_cpp_parameter_list.append(param.decl.name + ".mutable_data()")
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
    for old_param, new_param in  zip(function_adapted_params.function_infos.parameter_list.parameters, new_function_infos.parameter_list.parameters):
        if old_param.decl.is_c_array_fixed_size():
            expected_size = old_param.decl.c_array_size()
            lambda_code += f"{_i_}if ({new_param.decl.name}.shape()[0] != {expected_size})\n"
            lambda_code += f'{_i_}{_i_}throw std::runtime_error("param {new_param.decl.name} size should be {expected_size}");\n'
            # lambda_code += f"{_i_}auto buf_{new_param.decl.name} = {new_param.decl.name}.request()\n";
            # lambda_code += f"{_i_}auto ptr_{new_param.decl.name} = buf_{new_param.decl.name}.ptr\n";

    lambda_code += f""
    lambda_code += f""
    lambda_code += f"{_i_}return {function_adapted_params.function_infos.name}({adapted_cpp_parameter_list_str});\n"
    lambda_code += "};\n"

    function_adapted_params.cpp_adapter_code += lambda_code
    function_adapted_params.function_infos = new_function_infos
    function_adapted_params.lambda_to_call = lambda_name


def make_function_params_adapter(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> CppFunctionDeclWithAdaptedParams:
    function_adapted_params = CppFunctionDeclWithAdaptedParams(function_infos)
    _adapt_fixed_size_c_arrays(function_adapted_params, options, parent_struct_name)
    return function_adapted_params
