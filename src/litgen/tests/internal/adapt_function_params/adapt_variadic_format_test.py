from __future__ import annotations
from codemanip import code_utils

from srcmlcpp import srcmlcpp_main

import litgen
from litgen.internal import LitgenContext
from litgen.internal.adapted_types import AdaptedFunction


def make_pydef_code(code: str) -> str:
    options = litgen.LitgenOptions()
    lg_context = LitgenContext(options)
    function_decl = srcmlcpp_main.code_first_function_decl(options.srcmlcpp_options, code)
    adapted_function = AdaptedFunction(lg_context, function_decl, False)
    return adapted_function.str_pydef()


def test_adapt_variadic_format() -> None:
    expected_code = """
        m.def("log",
            [](LogLevel level, const char * const format)
            {
                auto Log_adapt_variadic_format = [](LogLevel level, const char * const format)
                {
                    Log(level, "%s", format);
                };

                Log_adapt_variadic_format(level, format);
            },     py::arg("level"), py::arg("format"));
    """

    code = "void Log(LogLevel level, char const* const format, ...);"
    pydef_code = make_pydef_code(code)
    code_utils.assert_are_codes_equal(pydef_code, expected_code)

    code = "void Log(LogLevel level, const char * const format, ...);"
    pydef_code = make_pydef_code(code)
    code_utils.assert_are_codes_equal(pydef_code, expected_code)

    expected_code = """
        m.def("log",
            [](LogLevel level, const char * format)
            {
                auto Log_adapt_variadic_format = [](LogLevel level, const char * format)
                {
                    Log(level, "%s", format);
                };

                Log_adapt_variadic_format(level, format);
            },     py::arg("level"), py::arg("format"));
    """

    code = "void Log(LogLevel level, const char * format, ...);"
    pydef_code = make_pydef_code(code)
    code_utils.assert_are_codes_equal(pydef_code, expected_code)
