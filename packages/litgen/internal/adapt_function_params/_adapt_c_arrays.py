import copy
from typing import List, Optional

from codemanip import code_utils

from srcmlcpp.srcml_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction, AdaptedParameter


def adapt_c_arrays(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
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
    options = adapted_function.options

    function_name = adapted_function.cpp_adapted_function.function_name
    flag_replace_const_c_array_by_std_array = code_utils.does_match_regexes(
        options.fn_params_replace_const_c_array_by_std_array__regexes, function_name
    )
    flag_replace_modifiable_c_array_by_boxed = code_utils.does_match_regexes(
        options.fn_params_replace_modifiable_c_array_by_boxed__regexes, function_name
    )

    if not flag_replace_const_c_array_by_std_array and not flag_replace_modifiable_c_array_by_boxed:
        return None

    needs_adapt = False

    for old_adapted_param in adapted_function.adapted_parameters():
        if old_adapted_param.cpp_element().decl.is_c_array_known_fixed_size(options.srcml_options):
            needs_adapt = True

    if not needs_adapt:
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)

    # old_function_params: List[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters
    old_function_params: List[AdaptedParameter] = adapted_function.adapted_parameters()

    new_function_params: List[CppParameter] = []
    for old_adapted_param in old_function_params:
        was_replaced = False
        old_cpp_decl = old_adapted_param.adapted_decl().cpp_element()
        if old_cpp_decl.is_c_array_known_fixed_size(options.srcml_options):

            if old_cpp_decl.is_const() and flag_replace_const_c_array_by_std_array:
                was_replaced = True
                # Create new calling param (const std::array &)
                new_adapted_decl = old_adapted_param.adapted_decl().c_array_fixed_size_to_const_std_array()

                new_param = CppParameter(old_adapted_param.cpp_element())  # copy.deepcopy(old_adapted_decl)
                new_param.decl = new_adapted_decl.cpp_element()
                new_function_params.append(new_param)
                # Fill adapted_cpp_parameter_list (those that will call the original C style function)
                lambda_adapter.adapted_cpp_parameter_list.append(new_adapted_decl.decl_name_cpp() + ".data()")

            elif not old_cpp_decl.is_const() and flag_replace_modifiable_c_array_by_boxed:
                array_size_int = old_cpp_decl.c_array_size_as_int(options.srcml_options)
                assert array_size_int is not None

                if array_size_int <= options.fn_params_replace_modifiable_c_array__max_size:

                    was_replaced = True

                    new_adapted_decls = old_adapted_param.adapted_decl().c_array_fixed_size_to_mutable_new_boxed_decls()

                    #
                    # Fill lambda_input_code and lambda_output_code
                    # and create new calling params (BoxedInt& for example)
                    #

                    # unsigned long output_raw[2];
                    # output_raw[0] = output_0.value;    // `lambda_input_code`
                    # output_raw[1] = output_1.value;

                    # output_0.value = output_raw[0];   // `lambda_output_code`
                    # output_1.value = output_raw[1];

                    old_adapted_param_renamed = copy.deepcopy(old_adapted_param)
                    old_adapted_param_renamed.cpp_element().decl.decl_name = (
                        old_adapted_param_renamed.cpp_element().decl.decl_name + "_raw"
                    )
                    lambda_adapter.lambda_input_code += old_adapted_param_renamed.cpp_element().str_code() + ";\n"

                    lambda_adapter.adapted_cpp_parameter_list.append(
                        old_adapted_param_renamed.cpp_element().decl.decl_name
                    )

                    for i, new_adapted_decl in enumerate(new_adapted_decls):
                        value_access = ".value" if old_adapted_param.adapted_decl().is_immutable_for_python() else ""
                        lambda_adapter.lambda_input_code += f"{old_adapted_param_renamed.adapted_decl().decl_name_cpp()}[{i}] = {new_adapted_decl.decl_name_cpp()}{value_access};\n"
                        lambda_adapter.lambda_output_code += f"{new_adapted_decl.decl_name_cpp()}{value_access} = {old_adapted_param_renamed.adapted_decl().decl_name_cpp()}[{i}];\n"

                        new_param = CppParameter(old_adapted_param.cpp_element())
                        new_param.decl = new_adapted_decl.cpp_element()
                        new_function_params.append(new_param)

        if not was_replaced:
            new_function_params.append(old_adapted_param.cpp_element())
            lambda_adapter.adapted_cpp_parameter_list.append(old_cpp_decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_fixed_size_c_arrays"

    return lambda_adapter
