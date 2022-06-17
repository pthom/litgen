from typing import Optional
import logging
import os, sys

import pytest  # type: ignore

_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")

from codemanip import code_utils
from litgen.options import LitgenOptions, code_style_implot
import litgen
from litgen.internal.function_adapt import make_adapted_function
from litgen.internal.function_adapt import adapt_c_arrays
from litgen.internal import module_pydef_generator, cpp_to_python
import srcmlcpp
from srcmlcpp.srcml_types import *

OPTIONS = litgen.options.code_style_implot()
OPTIONS.srcml_options.functions_api_prefixes = ["MY_API"]


def get_first_function_decl(code) -> Optional[CppFunctionDecl]:
    cpp_unit = srcmlcpp.code_to_cpp_unit(OPTIONS.srcml_options, code)
    for child in cpp_unit.block_children:
        if isinstance(child, CppFunctionDecl) or isinstance(child, CppFunction):
            return child
    return None


def test_make_function_params_adapter():
    def my_make_adapted_function(code):
        function_decl = get_first_function_decl(code)
        struct_name = ""
        adapted_function = make_adapted_function(function_decl, OPTIONS, struct_name)
        return adapted_function

    # Easy test with const
    code = """MY_API void foo(const int v[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.function_infos,
        "MY_API void foo(const std::array<int, 2>& v);",
    )

    # Less easy test with non const
    code = """MY_API void foo(unsigned long long v[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.function_infos,
        "MY_API void foo(BoxedUnsignedLongLong & v_0, BoxedUnsignedLongLong & v_1);",
    )

    # Full test with a mixture
    code = """MY_API void foo(bool flag, const double v[2], double outputs[2]);"""
    adapted_function = my_make_adapted_function(code)
    code_utils.assert_are_codes_equal(
        adapted_function.function_infos,
        "MY_API void foo(bool flag, const std::array<double, 2>& v, BoxedDouble & outputs_0, BoxedDouble & outputs_1);",
    )


def test_use_function_params_adapter_const():
    code = """MY_API void foo_const(const int input[2]);"""
    function_decl = get_first_function_decl(code)
    generated_code = module_pydef_generator._generate_function(function_decl, OPTIONS)
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
            },
            py::arg("input")
        );
    """,
    )


def test_use_function_params_adapter_non_const():
    code = """MY_API void foo_non_const(int output[2]);"""
    function_decl = get_first_function_decl(code)
    generated_code = module_pydef_generator._generate_function(function_decl, OPTIONS)
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
            },
            py::arg("output_0"), py::arg("output_1")
        );
    """,
    )


def test_mixture():
    code = """MY_API void foo(bool flag, const double v[2], double outputs[2]);"""
    function_decl = get_first_function_decl(code)
    generated_code = module_pydef_generator._generate_function(function_decl, OPTIONS)
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
                },
                py::arg("flag"), py::arg("v"), py::arg("outputs_0"), py::arg("outputs_1")
            );
    """,
    )


def test_mixture_no_replace():
    options = litgen.LitgenOptions()
    options.c_array_const_flag_replace = True
    options.c_array_modifiable_flag_replace = False

    code = """MY_API void foo(bool flag, const double v[2], double outputs[2]);"""
    function_decl = get_first_function_decl(code)
    generated_code = module_pydef_generator._generate_function(function_decl, options)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](bool flag, const std::array<double, 2>& v, double outputs[2])
            {
                auto foo_adapt_fixed_size_c_arrays = [](bool flag, const std::array<double, 2>& v, double outputs[2])
                {
                    auto r = foo(flag, v.data(), outputs);
                    return r;
                };

                return foo_adapt_fixed_size_c_arrays(flag, v, outputs);
            },
            py::arg("flag"), py::arg("v"), py::arg("outputs")
        );
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
    generated_code = litgen.generate_pydef(code, options)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        auto pyClassFoo = py::class_<Foo>
            (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            .def("thing",
                [](Foo & self, Point2 & out_0, Point2 & out_1)
                {
                    auto thing_adapt_fixed_size_c_arrays = [&self](Point2 & out_0, Point2 & out_1)
                    {
                        Point2 out_raw[2];
                        out_raw[0] = out_0;
                        out_raw[1] = out_1;

                        auto r = self.thing(out_raw);

                        out_0 = out_raw[0];
                        out_1 = out_raw[1];
                        return r;
                    };

                    return thing_adapt_fixed_size_c_arrays(out_0, out_1);
                },
                py::arg("out_0"), py::arg("out_1")
            )
            ;
    """,
    )
