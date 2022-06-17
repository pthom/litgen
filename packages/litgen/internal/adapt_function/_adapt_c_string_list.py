from typing import Optional, List
import copy

from litgen.generate_code import LitgenOptions, code_utils
from litgen.internal import cpp_to_python
from litgen.internal.adapt_function import AdaptedFunction
from litgen.internal.adapt_function._lambda_adapter import LambdaAdapter

from srcmlcpp.srcml_types import (
    CppFunctionDecl,
    CppParameter,
    CppParameterList,
    CppType,
    CppDecl,
)


def adapt_c_string_list(adapted_function: AdaptedFunction, options: LitgenOptions) -> Optional[LambdaAdapter]:
    """
    We want to adapt functions that use fixed size C string list like those:
        void foo(const char * const items[], int items_count);

    We will generate a lambda that looks like this
        [](const std::vector<std::string> & items)
        {
            auto foo_adapt_c_string_list = [](const std::vector<std::string> & items)
            {
                std::vector<const char *> items_ptrs;
                for (const auto& v: items)
                    items_ptrs.push_back(v.c_str());
                int items_count = static_cast<int>(items.size());

                return foo(items_ptrs.data(), items_count);
            };

            return foo_adapt_c_string_list(items);
        },
    """

    if not options.c_string_list_flag_replace:
        return None

    old_function_params: List[CppParameter] = adapted_function.function_infos.parameter_list.parameters

    def needs_adapt():
        param_0: CppParameter
        param_1: CppParameter
        for param_0, param_1 in code_utils.overlapping_pairs(old_function_params):
            if param_0.decl.is_c_string_list_ptr() and cpp_to_python.looks_like_size_param(param_1, options):
                return True
        return False

    if not needs_adapt():
        return None

    lambda_adapter = LambdaAdapter()

    _i_ = options.indent_cpp_spaces()

    lambda_adapter.new_function_infos = copy.deepcopy(adapted_function.function_infos)
    new_function_params = []

    def is_c_string_list(i: int):
        if i >= len(old_function_params) - 1:
            return False
        param = old_function_params[i]
        param_next = old_function_params[i + 1]
        r = param.decl.is_c_string_list_ptr() and cpp_to_python.looks_like_size_param(param_next, options)
        return r

    def is_c_string_list_size(i: int):
        if i < 1:
            return False
        param = old_function_params[i]
        param_previous = old_function_params[i - 1]
        r = param_previous.decl.is_c_string_list_ptr() and cpp_to_python.looks_like_size_param(param, options)
        return r

    for i, old_param in enumerate(old_function_params):
        was_replaced = False
        if is_c_string_list(i):
            was_replaced = True

            #
            # Create new calling param (std::vector<std::string> &)
            #
            new_param = copy.deepcopy(old_param)
            new_decl = new_param.decl
            if new_decl.is_c_array():
                new_decl.c_array_code = ""
            new_decl.initial_value_code = ""
            new_decl.cpp_type.specifiers = ["const"]
            new_decl.cpp_type.typenames = ["std::vector<std::string>"]
            new_decl.cpp_type.modifiers = ["&"]
            new_function_params.append(new_param)

            #
            # Fill lambda_input_code
            #
            # std::vector<const char *> items_ptrs;
            # for (const auto &s : items)                            // lambda_input_code
            #     items_ptrs.push_back(s.c_str());
            # int items_size = static_cast<int>(items.size());
            param_name = new_decl.decl_name
            vec_name = f"{param_name}_ptrs"
            next_param = old_function_params[i + 1]
            size_type = next_param.decl.cpp_type.typenames[0]
            size_name = next_param.decl.decl_name

            if size_type != "size_t" and size_type != "std::size_t":
                static_cast_str = f"static_cast<{size_type}>"
                casted_size_str = f"{static_cast_str}({param_name}.size())"
            else:
                casted_size_str = f"{param_name}.size()"

            lambda_adapter.lambda_input_code += f"std::vector<const char *> {vec_name};\n"
            lambda_adapter.lambda_input_code += f"for (const auto& v: {param_name})\n"
            lambda_adapter.lambda_input_code += f"{_i_}{vec_name}.push_back(v.c_str());\n"
            lambda_adapter.lambda_input_code += f"{size_type} {size_name} = {casted_size_str};\n"

            #
            # Fill adapted_cpp_parameter_list (those that will call the original C style function)
            #
            lambda_adapter.adapted_cpp_parameter_list.append(vec_name + ".data()")
            lambda_adapter.adapted_cpp_parameter_list.append(size_name)

        if is_c_string_list_size(i):
            continue

        if not was_replaced:
            new_function_params.append(old_param)
            lambda_adapter.adapted_cpp_parameter_list.append(old_param.decl.decl_name)

    lambda_adapter.new_function_infos.parameter_list.parameters = new_function_params

    lambda_adapter.lambda_name = adapted_function.function_infos.function_name + "_adapt_c_string_list"

    return lambda_adapter
