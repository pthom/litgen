from __future__ import annotations
import copy
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types import CppParameter

from litgen.internal import boxed_python_type
from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction, AdaptedParameter


def adapt_modifiable_immutable(adapted_function: AdaptedFunction) -> Optional[LambdaAdapter]:
    """
    We want to adapt functions params that use modifiable pointer or reference to a type that is immutable in python.
    For example
        `int foo(int* value)`
        `void foo(float& value)`
        `void foo(string& value)`

    On the C++ side, these params are modifiable by the function. We need to box them into a Boxed type
    to ensure any modification made by C++ is visible when going back to Python.

    Note: immutable data types in python are
        - Int, Float, String (currently handled here)
        - Complex, Bytes (not yet handed here)
        - Tuple (not handled here)

    For the function
        int foo(int* value)
    We will generate an adapter lambda that looks like
        [](int* input)
        {
            auto foo_adapt_pointer_to_immutable = [](BoxedInt& input)
            {
                auto r = foo(& input.value);
                return  r;
            };
            return foo_adapt_modifiable_immutable(input);
        }
    """
    options = adapted_function.options

    function_name = adapted_function.cpp_adapted_function.function_name
    if not code_utils.does_match_regex(options.fn_params_replace_modifiable_immutable_by_boxed__regex, function_name):
        return None

    needs_adapt = False

    for old_adapted_param in adapted_function.adapted_parameters():
        if old_adapted_param.is_modifiable_python_immutable_ref_or_pointer():
            needs_adapt = True

    if not needs_adapt:
        return None

    lambda_adapter = LambdaAdapter()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.cpp_adapted_function)

    # old_function_params: List[CppParameter] = adapted_function.cpp_adapted_function.parameter_list.parameters
    old_function_params: list[AdaptedParameter] = adapted_function.adapted_parameters()

    new_function_params: list[CppParameter] = []
    for old_adapted_param in old_function_params:
        was_replaced = False

        if old_adapted_param.is_modifiable_python_immutable_ref_or_pointer():
            was_replaced = True

            is_pointer = old_adapted_param.cpp_element().decl.cpp_type.modifiers == ["*"]

            # For signatures like
            #       void foo(bool * flag = NULL);
            # the python param type will be type Optional[BoxedBool]
            def compute_is_optional_boxed_type(old_adapted_param=old_adapted_param, is_pointer=is_pointer) -> bool:  # type: ignore
                initial_value_cpp = old_adapted_param.cpp_element().decl.initial_value_code
                is_initial_value_null = initial_value_cpp in ["NULL", "nullptr"]
                return is_pointer and is_initial_value_null

            is_optional_type = compute_is_optional_boxed_type()

            #
            # Create new calling param (BoxedType<T>)
            #
            new_param = copy.deepcopy(old_adapted_param.cpp_element())
            cpp_type_str = old_adapted_param.cpp_element().decl.cpp_type.name_without_modifier_specifier()

            boxed_type_name = boxed_python_type.registered_boxed_type_name(adapted_function.lg_context, cpp_type_str)

            new_decl = new_param.decl
            if is_optional_type:
                new_decl.cpp_type.typenames = [boxed_type_name]
                new_decl.cpp_type.modifiers = ["*"]
                new_decl.initial_value_code = "nullptr"
            else:
                new_decl.cpp_type.typenames = [boxed_type_name]
                new_decl.cpp_type.modifiers = ["&"]
            new_decl.cpp_type.specifiers = []
            new_function_params.append(new_param)

            #
            # Fill lambda_input_code
            #
            param_original_type = old_adapted_param.cpp_element().full_type()
            param_name_value = old_adapted_param.cpp_element().decl.decl_name + "_boxed_value"
            param_name = old_adapted_param.cpp_element().decl.decl_name
            _i_ = adapted_function.options._indent_cpp_spaces()

            if is_optional_type:
                lambda_input_code = f"""
                    {param_original_type} {param_name_value} = nullptr;
                    if ({param_name} != nullptr)
                    {_i_}{param_name_value} = & ({param_name}->value);
                """
            else:
                if is_pointer:
                    lambda_input_code = f"""
                        {param_original_type} {param_name_value} = & ({param_name}.value);
                        """
                else:
                    lambda_input_code = f"""
                        {param_original_type} {param_name_value} = {param_name}.value;
                        """

            lambda_adapter.lambda_input_code += (
                code_utils.unindent_code(lambda_input_code, flag_strip_empty_lines=True) + "\n"
            )

            #
            # Fill adapted_cpp_parameter_list (those that will call the original C style function)
            #
            lambda_adapter.adapted_cpp_parameter_list.append(f"{param_name_value}")

        if not was_replaced:
            new_function_params.append(old_adapted_param.cpp_element())
            lambda_adapter.adapted_cpp_parameter_list.append(old_adapted_param.cpp_element().decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_modifiable_immutable"

    return lambda_adapter
