from typing import List, Optional
import copy

from litgen.generate_code import CodeStyleOptions
from litgen.internal.cpp_function_adapted_params import (
    CppFunctionDeclWithAdaptedParams,
    LambdaAdapter,
)

from srcmlcpp.srcml_types import CppParameter


def adapt_c_arrays(
    function_adapted_params: CppFunctionDeclWithAdaptedParams, options: CodeStyleOptions
) -> Optional[LambdaAdapter]:
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

    if not options.c_array_const_flag_replace and not options.c_array_modifiable_flag_replace:
        return None

    needs_adapt = False

    for old_param in function_adapted_params.function_infos.parameter_list.parameters:
        if old_param.decl.is_c_array_fixed_size():
            needs_adapt = True

    if not needs_adapt:
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(function_adapted_params.function_infos)
    old_function_params: List[CppParameter] = function_adapted_params.function_infos.parameter_list.parameters
    new_function_params = []
    for old_param in old_function_params:
        was_replaced = False
        if old_param.decl.is_c_array_fixed_size():

            if old_param.decl.is_const() and options.c_array_const_flag_replace:
                was_replaced = True
                # Create new calling param (const std::array &)
                new_decl = old_param.decl.c_array_fixed_size_to_std_array()
                new_param = copy.deepcopy(old_param)
                new_param.decl = new_decl
                new_function_params.append(new_param)
                # Fill adapted_cpp_parameter_list (those that will call the original C style function)
                lambda_adapter.adapted_cpp_parameter_list.append(new_decl.decl_name + ".data()")

            if not old_param.decl.is_const() and options.c_array_modifiable_flag_replace:
                array_size = old_param.decl.c_array_size()
                assert array_size is not None

                if array_size <= options.c_array_modifiable_max_size:

                    was_replaced = True

                    new_decls = old_param.decl.c_array_fixed_size_to_new_boxed_decls()

                    #
                    # Fill lambda_input_code and lambda_output_code
                    # and create new calling params (BoxedInt& for example)
                    #

                    # unsigned long output_raw[2];
                    # output_raw[0] = output_0.value;    // `lambda_input_code`
                    # output_raw[1] = output_1.value;

                    # output_0.value = output_raw[0];   // `lambda_output_code`
                    # output_1.value = output_raw[1];

                    old_param_renamed = copy.deepcopy(old_param)
                    old_param_renamed.decl.decl_name = old_param_renamed.decl.decl_name + "_raw"
                    lambda_adapter.lambda_input_code += (
                        old_param_renamed.decl.str_code() + f"[{len(new_decls)}]" + ";\n"
                    )

                    lambda_adapter.adapted_cpp_parameter_list.append(old_param_renamed.decl.decl_name)

                    for i, new_decl in enumerate(new_decls):
                        value_access = ".value" if old_param.decl.is_immutable_for_python() else ""
                        lambda_adapter.lambda_input_code += (
                            f"{old_param_renamed.decl.decl_name}[{i}] = {new_decl.decl_name}{value_access};\n"
                        )
                        lambda_adapter.lambda_output_code += (
                            f"{new_decl.decl_name}{value_access} = {old_param_renamed.decl.decl_name}[{i}];\n"
                        )

                        new_param = copy.deepcopy(old_param)
                        new_param.decl = new_decl
                        new_function_params.append(new_param)

        if not was_replaced:
            new_function_params.append(old_param)
            lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = function_adapted_params.function_infos.function_name + "_adapt_fixed_size_c_arrays"

    return lambda_adapter
