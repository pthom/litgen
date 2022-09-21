from srcmlcpp.srcml_types import *
from srcmlcpp import srcmlcpp_main

import litgen
from litgen import LitgenOptions
from litgen.internal.adapted_types import AdaptedFunction


def make_pydef_code(code) -> str:
    options = litgen.options.LitgenOptions()
    function_decl = srcmlcpp_main.code_first_function_decl(options.srcml_options, code)
    adapted_function = AdaptedFunction(options, function_decl, False)
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
