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
        IMPLOT_TMP int Foo1(const T* values, int count);
        """

        expected_lambda_code_naive = """
            [](const T* values, int count)
            {
                return Foo1(values, count);
            },
        """

        expected_lambda_code_buffer = """
            [](const py::array & values)
            {
                // convert values (py::array&) to C standard buffer
                const void* values_buffer =  values.data();
                int values_count = values.shape()[0];
                    
                return Foo1(values_buffer, values_count);
            },
        """

        options.buffer_flag_replace_by_array = False
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_naive )

        options.buffer_flag_replace_by_array = True
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_one_buffer()

    def test_with_four_buffers():
        function_decl = """
            IMPLOT_TMP int Foo4(const T* values_x, const T* values_y, const T* values_z, T* values_w, int count);
        """

        expected_lambda_code_buffer = """
            [](const py::array & values_x, const py::array & values_y, const py::array & values_z, py::array & values_w)
            {
                // convert values_x (py::array&) to C standard buffer
                const void* values_x_buffer =  values_x.data();
                int values_x_count = values_x.shape()[0];
                    
                // convert values_y (py::array&) to C standard buffer
                const void* values_y_buffer =  values_y.data();
                int values_y_count = values_y.shape()[0];
                    
                // convert values_z (py::array&) to C standard buffer
                const void* values_z_buffer =  values_z.data();
                int values_z_count = values_z.shape()[0];
                    
                // convert values_w (py::array&) to C standard buffer
                void* values_w_buffer =  values_w.data();
                int values_w_count = values_w.shape()[0];
                    
                return Foo4(values_x_buffer, values_y_buffer, values_z_buffer, values_w_buffer, values_x_count);
            },
        """
        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_four_buffers()

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

    test_with_variadic_fmt()

    def test_with_modifiable_int():
        function_decl = """
            // Modify an array by adding a value to its elements
            IMPLOT_API inline void add_inside_array(int* array, int array_size, int number_to_add);
        """

        expected_lambda_code_buffer = """
            [](py::array & array, int number_to_add)
            {
                // convert array (py::array&) to C standard buffer
                int* array_buffer = (int*) array.data();
                int array_count = array.shape()[0];
                    
                return add_inside_array(array_buffer, array_count, number_to_add);
            },
    """

        options.buffer_flag_replace_by_array = True
        options.buffer_inner_types = ["T", "void", "int"]
        generated_code = make_lambda_code(function_decl)
        code_utils.assert_are_codes_equal( generated_code, expected_lambda_code_buffer )

    test_with_modifiable_int()
