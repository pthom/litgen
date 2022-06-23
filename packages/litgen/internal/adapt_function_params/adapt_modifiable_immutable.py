import copy
from typing import List, Optional

from srcmlcpp.srcml_types import CppParameter

from litgen.internal.adapt_function_params._lambda_adapter import LambdaAdapter
from litgen.internal.adapted_types import AdaptedFunction, AdaptedParameter
from litgen.internal.boxed_immutable_python_type import BoxedImmutablePythonType


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
    if not options.fn_params_adapt_modifiable_immutable:
        return None

    needs_adapt = False

    for old_adapted_param in adapted_function.adapted_parameters():
        if old_adapted_param.is_modifiable_python_immutable():
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

        if old_adapted_param.is_modifiable_python_immutable():
            was_replaced = True

            #
            # Create new calling param (BoxedType<T>)
            #
            new_param = copy.deepcopy(old_adapted_param.cpp_element())
            boxed_type = BoxedImmutablePythonType(
                old_adapted_param.cpp_element().decl.cpp_type.name_without_modifier_specifier()
            )
            new_decl = new_param.decl
            new_decl.cpp_type.typenames = [boxed_type.boxed_type_name()]
            new_decl.cpp_type.specifiers = []
            new_decl.cpp_type.modifiers = ["&"]
            new_function_params.append(new_param)

            #
            # Fill lambda_input_code: Not needed
            #

            #
            # Fill adapted_cpp_parameter_list (those that will call the original C style function)
            #
            needs_deref = old_adapted_param.cpp_element().decl.cpp_type.modifiers == ["*"]
            param_name = new_param.decl.decl_name
            if needs_deref:
                lambda_adapter.adapted_cpp_parameter_list.append(f"& {param_name}.value")
            else:
                lambda_adapter.adapted_cpp_parameter_list.append(f"{param_name}.value")

        if not was_replaced:
            new_function_params.append(old_adapted_param.cpp_element())
            lambda_adapter.adapted_cpp_parameter_list.append(old_adapted_param.cpp_element().decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.cpp_adapted_function.function_name + "_adapt_modifiable_immutable"

    return lambda_adapter
