from typing import Optional, List
import copy
import enum
from dataclasses import dataclass

from litgen.generate_code import CodeStyleOptions, generate_pydef, code_utils
from litgen.internal import cpp_to_python
from litgen.internal.function_params_adapter import CppFunctionDeclWithAdaptedParams

from srcmlcpp.srcml_types import CppFunctionDecl, CppParameter, CppParameterList, CppType, CppDecl


def adapt_c_arrays(function_adapted_params: CppFunctionDeclWithAdaptedParams,
                   options: CodeStyleOptions,
                   parent_struct_name: str = ""
                   ) -> CppFunctionDeclWithAdaptedParams:
    """
    We want to adapt functions that use fixed size C arrays like those:
        `void foo_const(const int input[2])` or `void foo_non_const(int output[2])`

    For const parameters e.g. `int foo_const(const int input[2])`, we will generate a lambda that looks like
        [](const std::array<int, 2>& input)
        {
            auto foo_const_adapt_fixed_size_c_arrays = [](const std::array<int, 2>& input)
            {
                return foo_const(input.data()); // Sigh, this might differ for void functions!
            };
            return foo_const_adapt_fixed_size_c_arrays(input); // This might differ for void functions!
        }

    For non const parameters, e.g. `void foo_non_const(int output[2])` we will generate a lambda that looks like:
            [](BoxedInt & output_0, BoxedInt & output_1)
            {
                auto foo_non_const_adapt_fixed_size_c_arrays = [](BoxedInt & output_0, BoxedInt & output_1)
                {
                    int output_raw[2];
                    output_raw[0] = output_0.value;
                    output_raw[1] = output_1.value;

                    foo_non_const(output_raw);

                    output_0.value = output_raw[0];
                    output_1.value = output_raw[1];
                };

                foo_non_const_adapt_fixed_size_c_arrays(output_0, output_1);
            }
    """
    needs_adapt = False
    for old_param in function_adapted_params.function_infos.parameter_list.parameters:
        if old_param.decl.is_c_array_fixed_size():
            needs_adapt = True

    if not needs_adapt:
        return

    new_function_infos = copy.deepcopy(function_adapted_params.function_infos)
    old_function_params: List[CppParameter] = function_adapted_params.function_infos.parameter_list.parameters
    new_function_params = []
    adapted_cpp_parameter_list = []
    lambda_input_code = ""
    lambda_output_code = ""
    for old_param in old_function_params:
        if old_param.decl.is_c_array_fixed_size():
            if old_param.decl.is_const():
                new_decl = old_param.decl.c_array_fixed_size_to_std_array()
                new_param = copy.deepcopy(old_param)
                new_param.decl = new_decl
                new_function_params.append(new_param)
                adapted_cpp_parameter_list.append(new_decl.name + ".data()")
            else:
                new_decls = old_param.decl.c_array_fixed_size_to_new_modifiable_decls()

                # unsigned long output_raw[2];
                # output_raw[0] = output_0.value;    // `lambda_input_code`
                # output_raw[1] = output_1.value;

                # output_0.value = output_raw[0];   // `lambda_output_code`
                # output_1.value = output_raw[1];

                old_param_renamed = copy.deepcopy(old_param)
                old_param_renamed.decl.name = old_param_renamed.decl.name_c_array() + "_raw"
                lambda_input_code += old_param_renamed.decl.str_code() + f"[{len(new_decls)}]" + ";\n"

                adapted_cpp_parameter_list.append(old_param_renamed.decl.name)

                for i, new_decl in enumerate(new_decls):
                    lambda_input_code += f"{old_param_renamed.decl.name}[{i}] = {new_decl.name}.value;\n"
                    lambda_output_code += f"{new_decl.name}.value = {old_param_renamed.decl.name}[{i}];\n"

                    new_param = copy.deepcopy(old_param)
                    new_param.decl = new_decl
                    new_function_params.append(new_param)
        else:
            new_function_params.append(old_param)
            adapted_cpp_parameter_list.append(old_param.decl.name)
    new_function_infos.parameter_list.parameters = new_function_params

    lambda_name = function_adapted_params.function_infos.name + "_adapt_fixed_size_c_arrays"
    capture_this = "this" if len(parent_struct_name) > 0 else ""
    adapted_python_parameter_list_str = new_function_infos.parameter_list.str_code()
    adapted_cpp_parameter_list_str = ", ".join(adapted_cpp_parameter_list)

    _i_ = options.indent_cpp_spaces()
    lambda_code = ""
    lambda_code += f"auto {lambda_name} = [{capture_this}]({adapted_python_parameter_list_str})\n"
    lambda_code += "{\n"
    fn_return_type = function_adapted_params.function_infos.full_return_type(options.srcml_options)
    return_code = "" if fn_return_type == "void" else "return "

    if len(lambda_input_code) > 0:
        lambda_code += code_utils.indent_code(lambda_input_code, indent_str=options.indent_cpp_spaces()) + "\n"
    lambda_code += f"{_i_}{return_code}{function_adapted_params.function_infos.name}({adapted_cpp_parameter_list_str});\n"
    if len(lambda_output_code) > 0:
        lambda_code += "\n" + code_utils.indent_code(lambda_output_code, indent_str=options.indent_cpp_spaces())
    lambda_code += "};\n"

    function_adapted_params.cpp_adapter_code += lambda_code
    function_adapted_params.function_infos = new_function_infos
    function_adapted_params.lambda_to_call = lambda_name
