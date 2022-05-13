import os, sys;

import code_utils

_THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import code_replacements
from code_types import *
from options import CodeStyleOptions, code_style_implot, code_style_immvision
import function_parser
import function_wrapper_lambda


def test_make_function_wrapper_lambda():
    options = code_style_implot()

    def make_lambda_code(code):
        fn_info = function_parser.parse_one_function_declaration(code, options)
        lambda_code = function_wrapper_lambda.make_function_wrapper_lambda(fn_info, options)
        return lambda_code

    def easy_test():
        code = 'IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt = "%.3f");'
        code_utils.assert_are_codes_equal(
            make_lambda_code(code),
            """
            [](ImAxis axis, const char* fmt = "%.3f")
            {
                SetupAxisFormat(axis, fmt);
            },
            """)

    easy_test()


    def test_with_one_buffer():
        function_decl = """
        IMPLOT_TMP int PlotScatter(const char* label_id, const T* values, int count, double xscale=1, double x0=0, int offset=0, int stride=sizeof(T));
        """

        expected_lambda_code_naive = """
        [](const char* label_id, const T* values, int count, double xscale = 1, double x0 = 0, int offset = 0, int stride = sizeof(T))
        {
            return PlotScatter(label_id, values, count, xscale, x0, offset, stride);
        },
        """

        expected_lambda_code_buffer = """
        [](const char* label_id, const py::array & values, double xscale = 1, double x0 = 0, int offset = 0, int stride = -1)
        {
            // convert values (py::array&) to C standard buffer
            const void* values_buffer = values.data();
            int values_count = values.shape()[0];

            // process stride default value (which was a sizeof in C++)
            int values_stride = stride;
            if (values_stride == -1)
                values_stride = (int)values.itemsize();

            return PlotScatter(label_id, values_buffer, values_count, xscale, x0, offset, values_stride);
        },
        """

        options.buffer_flag_replace_by_array = False
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_naive )

        options.buffer_flag_replace_by_array = True
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_one_buffer()

    def test_with_two_buffers():
        function_decl = """
        IMPLOT_TMP void PlotScatter(const char* label_id, const T* xs, const T* ys, int count, int offset=0, int stride=sizeof(T));
        """

        expected_lambda_code_buffer = """
        [](const char* label_id, const py::array & xs, const py::array & ys, int offset = 0, int stride = -1)
        {
            // convert xs (py::array&) to C standard buffer
            const void* xs_buffer = xs.data();
            int xs_count = xs.shape()[0];
                
            // convert ys (py::array&) to C standard buffer
            const void* ys_buffer = ys.data();
            int ys_count = ys.shape()[0];
                
            // process stride default value (which was a sizeof in C++)
            int xs_stride = stride;
            if (xs_stride == -1)
                xs_stride = (int)xs.itemsize();
                
            PlotScatter(label_id, xs_buffer, ys_buffer, xs_count, offset, xs_stride);
        },
        """
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_two_buffers()

    def test_with_variadic_fmt():
        function_decl = """
            IMPLOT_API void TagX(double x, const ImVec4& color, const char* fmt, ...)           IM_FMTARGS(3);
        """

        expected_lambda_code_buffer = """
            [](double x, const ImVec4& color, const char* fmt)
            {
                 TagX(x, color, "%s", fmt);
            },
        """

        options.buffer_flag_replace_by_array = True
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )
        # print("\n\n\n" + function_decl)
        # print("\n\n\n" + make_lambda_code(function_decl))
        # assert False

    test_with_variadic_fmt()
