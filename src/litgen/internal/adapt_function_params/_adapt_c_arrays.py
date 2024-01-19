from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction, AdaptedParameter


def adapt_c_arrays(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    """
    We want to adapt functions that use fixed size C arrays like those:
        `void foo_const(const int input[2])` or `void foo_non_const(int output[2])`

    Two possibilities:
    1.  Using std::array, for const c-array parameter, e.g.
            `int foo(const int input[2])`,
        we will generate a python functions whose signature is:
            def foo(self, values: List[int]) -> None:
                pass
        thanks to a lambda that looks like
            [](const std::array<int, 2>& input)
            {
                auto foo_const_adapt_fixed_size_c_arrays = [](const std::array<int, 2>& input)
                {
                    return foo_const(input.data()); // Sigh, this might differ for void functions!
                };
                return foo_const_adapt_fixed_size_c_arrays(input); // This might differ for void functions!
            }

    2.  Duplicating the params for non const c-array parameter, e.g.
            `void foo_non_const(float output[2])`
        we will generate a python function whose signature is:
           def truc(self, input_0: BoxedFloat, input_1: BoxedFloat)
        thanks to a lambda that looks like:
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

    def shall_replace_by_boxed(param: AdaptedParameter) -> bool:
        flag_replace_by_boxed = code_utils.does_match_regex(
            options.fn_params_replace_c_array_modifiable_by_boxed__regex, function_name
        )
        cpp_decl = param.adapted_decl().cpp_element()
        is_c_array_known_fixed_size = cpp_decl.is_c_array_known_fixed_size()
        is_modifiable = not cpp_decl.is_const()
        return is_modifiable and is_c_array_known_fixed_size and flag_replace_by_boxed

    def shall_replace_by_std_array(param: AdaptedParameter) -> bool:
        flag_replace_by_std_array = code_utils.does_match_regex(
            options.fn_params_replace_c_array_const_by_std_array__regex, function_name
        )
        cpp_decl = param.adapted_decl().cpp_element()
        is_c_array_known_fixed_size = cpp_decl.is_c_array_known_fixed_size()
        is_const = cpp_decl.is_const()
        return is_const and is_c_array_known_fixed_size and flag_replace_by_std_array

    def needs_adapt_at_least_one_param() -> bool:
        needs_adapt_r = False
        for param in adapted_function.adapted_parameters():
            if shall_replace_by_boxed(param):
                needs_adapt_r = True
            if shall_replace_by_std_array(param):
                needs_adapt_r = True
        return needs_adapt_r

    if not needs_adapt_at_least_one_param():
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)

    # old_function_params: List[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters
    old_function_params: list[AdaptedParameter] = adapted_function.adapted_parameters()

    new_function_params: list[CppParameter] = []
    for old_adapted_param in old_function_params:
        was_replaced = False
        old_cpp_decl = old_adapted_param.adapted_decl().cpp_element()
        if old_cpp_decl.is_c_array_known_fixed_size():
            if shall_replace_by_std_array(old_adapted_param):
                was_replaced = True
                # Create new calling param (const std::array &)
                new_adapted_decl = old_adapted_param.adapted_decl().c_array_fixed_size_to_const_std_array()

                new_param = CppParameter(old_adapted_param.cpp_element())
                new_param.decl = new_adapted_decl.cpp_element()
                new_function_params.append(new_param)
                # Fill adapted_cpp_parameter_list (those that will call the original C style function)
                lambda_adapter.adapted_cpp_parameter_list.append(new_adapted_decl.decl_name_cpp() + ".data()")

            elif shall_replace_by_boxed(old_adapted_param):
                array_size_int = old_cpp_decl.c_array_size_as_int()
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
