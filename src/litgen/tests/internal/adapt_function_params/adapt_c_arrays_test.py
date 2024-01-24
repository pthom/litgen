from __future__ import annotations
from typing import Optional

from codemanip import code_utils

from srcmlcpp import srcmlcpp_main

import litgen
from litgen import LitgenOptions
from litgen.internal import LitgenContext
from litgen.internal.adapted_types import AdaptedFunction
from litgen.litgen_generator import LitgenGeneratorTestsHelper


def gen_pydef_code(code: str, options: Optional[LitgenOptions] = None) -> str:
    if options is None:
        options = litgen.LitgenOptions()
        options.srcmlcpp_options.functions_api_prefixes = "MY_API"

    cpp_function = srcmlcpp_main.code_first_function_decl(options.srcmlcpp_options, code)
    adapted_function = AdaptedFunction(LitgenContext(options), cpp_function, False)
    generated_code = adapted_function.str_pydef()
    return generated_code


def my_make_adapted_function(code: str) -> AdaptedFunction:
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"

    function_decl = srcmlcpp_main.code_first_function_decl(options.srcmlcpp_options, code)
    adapted_function = AdaptedFunction(LitgenContext(options), function_decl, False)
    return adapted_function


def test_make_function_params_adapter() -> None:
    # Easy test with const
    code = """MY_API void foo(const int v[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.cpp_adapted_function,
        "void foo(const std::array<int, 2>& v);",
    )

    # Less easy test with non const
    code = """MY_API void foo(unsigned long long v[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.cpp_adapted_function,
        "void foo(BoxedUnsignedLongLong & v_0, BoxedUnsignedLongLong & v_1);",
    )

    # Full test with a mixture
    code = """MY_API void foo(bool flag, const double v[2], double outputs[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.cpp_adapted_function,
        "void foo(bool flag, const std::array<double, 2>& v, BoxedDouble & outputs_0, BoxedDouble & outputs_1);",
    )


def test_use_function_params_adapter_const():
    code = """MY_API void foo_const(const int input[2]);"""
    generated_code = gen_pydef_code(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo_const",
            [](const std::array<int, 2>& input)
            {
                auto foo_const_adapt_fixed_size_c_arrays = [](const std::array<int, 2>& input)
                {
                    foo_const(input.data());
                };

                foo_const_adapt_fixed_size_c_arrays(input);
            },     py::arg("input"));
        """,
    )


def test_use_function_params_adapter_non_const():
    code = """MY_API void foo_non_const(int output[2]);"""
    generated_code = gen_pydef_code(code)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo_non_const",
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
            },     py::arg("output_0"), py::arg("output_1"));
        """,
    )


def test_mixture():
    code = """MY_API void foo(bool flag, const double v[2], double outputs[2]);"""
    generated_code = gen_pydef_code(code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](bool flag, const std::array<double, 2>& v, BoxedDouble & outputs_0, BoxedDouble & outputs_1)
            {
                auto foo_adapt_fixed_size_c_arrays = [](bool flag, const std::array<double, 2>& v, BoxedDouble & outputs_0, BoxedDouble & outputs_1)
                {
                    double outputs_raw[2];
                    outputs_raw[0] = outputs_0.value;
                    outputs_raw[1] = outputs_1.value;

                    foo(flag, v.data(), outputs_raw);

                    outputs_0.value = outputs_raw[0];
                    outputs_1.value = outputs_raw[1];
                };

                foo_adapt_fixed_size_c_arrays(flag, v, outputs_0, outputs_1);
            },     py::arg("flag"), py::arg("v"), py::arg("outputs_0"), py::arg("outputs_1"));
        """,
    )


def test_mixture_no_replace():
    options = litgen.LitgenOptions()
    options.fn_params_replace_c_array_const_by_std_array__regex = r".*"
    options.fn_params_replace_c_array_modifiable_by_boxed__regex = ""

    code = """void foo(bool flag, const double v[2], double outputs[2]);"""
    generated_code = gen_pydef_code(code, options)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](bool flag, const std::array<double, 2>& v, double outputs[2])
            {
                auto foo_adapt_fixed_size_c_arrays = [](bool flag, const std::array<double, 2>& v, double outputs[2])
                {
                    foo(flag, v.data(), outputs);
                };

                foo_adapt_fixed_size_c_arrays(flag, v, outputs);
            },     py::arg("flag"), py::arg("v"), py::arg("outputs"));
        """,
    )


def test_in_method():
    code = """
        struct Foo
        {
            IMGUI_API bool thing(Point2 out[2]);
        };
    """
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "IMGUI_API"
    options.original_location_flag_show = True
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        auto pyClassFoo =
            py::class_<Foo>    // Line:2
                (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            .def("thing",    // Line:4
                [](Foo & self, Point2 & out_0, Point2 & out_1) -> bool
                {
                    auto thing_adapt_fixed_size_c_arrays = [&self](Point2 & out_0, Point2 & out_1) -> bool
                    {
                        Point2 out_raw[2];
                        out_raw[0] = out_0;
                        out_raw[1] = out_1;

                        auto lambda_result = self.thing(out_raw);

                        out_0 = out_raw[0];
                        out_1 = out_raw[1];
                        return lambda_result;
                    };

                    return thing_adapt_fixed_size_c_arrays(out_0, out_1);
                },     py::arg("out_0"), py::arg("out_1"))
            ;
        """,
    )
