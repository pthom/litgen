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
    options.functions_api_prefixes = ["MY_API"]

    def make_lambda_code(code):
        fn_info = function_parser.parse_one_function_declaration(code, options)
        lambda_code = function_wrapper_lambda.make_function_wrapper_lambda(fn_info, options)
        return lambda_code

    def easy_test():
        code = 'MY_API void SetupAxisFormat(ImAxis axis, const char* fmt = "%.3f");'
        code_utils.assert_are_codes_equal(
            make_lambda_code(code),
            """
                [](ImAxis axis, const char* fmt = "%.3f")
                {
                    SetupAxisFormat(axis, fmt);
                },
            """)

    easy_test()

    def test_with_one_const_buffer():
        function_decl = """
            MY_API inline int8_t test_with_one_const_buffer(const int8_t* values, int count)
        """

        expected_lambda_code_buffer = """
            [](const py::array & values)
            {
                // convert values (py::array&) to C standard buffer (const)
                const void* values_buffer = values.data();
                int values_count = values.shape()[0];
            
                char array_type = values.dtype().char_();
                if (array_type != 'b')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a buffer of native type:
                                        const int8_t*
                                    Which is equivalent to
                                        b
                                    (using py::array::dtype().char_() as an id)
                        )msg"));
                return test_with_one_const_buffer(static_cast<const int8_t*>(values_buffer), values_count);
            },
        """

        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_one_const_buffer()

    def test_with_one_nonconst_buffer():
        function_decl = """
            MY_API inline void test_with_one_nonconst_buffer(int8_t* values, int count)
        """

        expected_lambda_code_buffer = """
            [](py::array & values)
            {
                // convert values (py::array&) to C standard buffer (mutable)
                void* values_buffer = values.mutable_data();
                int values_count = values.shape()[0];
            
                char array_type = values.dtype().char_();
                if (array_type != 'b')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a buffer of native type:
                                        int8_t*
                                    Which is equivalent to
                                        b
                                    (using py::array::dtype().char_() as an id)
                        )msg"));
                test_with_one_nonconst_buffer(static_cast<int8_t*>(values_buffer), values_count);
            },
        """

        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_one_nonconst_buffer()

    def test_with_two_template_buffers():
        function_decl = """
            MY_API template<typename T> inline int test_with_two_template_buffers(const T* values1, T* values2, int count)
        """

        expected_lambda_code_buffer = """
            [](const py::array & values1, py::array & values2)
            {
                // convert values1 (py::array&) to C standard buffer (const)
                const void* values1_buffer = values1.data();
                int values1_count = values1.shape()[0];
            
                // convert values2 (py::array&) to C standard buffer (mutable)
                void* values2_buffer = values2.mutable_data();
                int values2_count = values2.shape()[0];
            
                char array_type = values1.dtype().char_();
                if (array_type == 'B')
                    return test_with_two_template_buffers(static_cast<const uint8_t*>(values1_buffer), static_cast<uint8_t*>(values2_buffer), values1_count);
                if (array_type == 'b')
                    return test_with_two_template_buffers(static_cast<const int8_t*>(values1_buffer), static_cast<int8_t*>(values2_buffer), values1_count);
                if (array_type == 'H')
                    return test_with_two_template_buffers(static_cast<const uint16_t*>(values1_buffer), static_cast<uint16_t*>(values2_buffer), values1_count);
                if (array_type == 'h')
                    return test_with_two_template_buffers(static_cast<const int16_t*>(values1_buffer), static_cast<int16_t*>(values2_buffer), values1_count);
                if (array_type == 'I')
                    return test_with_two_template_buffers(static_cast<const uint32_t*>(values1_buffer), static_cast<uint32_t*>(values2_buffer), values1_count);
                if (array_type == 'i')
                    return test_with_two_template_buffers(static_cast<const int32_t*>(values1_buffer), static_cast<int32_t*>(values2_buffer), values1_count);
                if (array_type == 'L')
                    return test_with_two_template_buffers(static_cast<const uint64_t*>(values1_buffer), static_cast<uint64_t*>(values2_buffer), values1_count);
                if (array_type == 'l')
                    return test_with_two_template_buffers(static_cast<const int64_t*>(values1_buffer), static_cast<int64_t*>(values2_buffer), values1_count);
                if (array_type == 'f')
                    return test_with_two_template_buffers(static_cast<const float*>(values1_buffer), static_cast<float*>(values2_buffer), values1_count);
                if (array_type == 'd')
                    return test_with_two_template_buffers(static_cast<const double*>(values1_buffer), static_cast<double*>(values2_buffer), values1_count);
                if (array_type == 'g')
                    return test_with_two_template_buffers(static_cast<const long double*>(values1_buffer), static_cast<long double*>(values2_buffer), values1_count);
            
                // If we arrive here, the array type is not supported!
                throw std::runtime_error(std::string("Bad array type: ") + array_type );
            },
        """

        code_utils.assert_are_codes_equal( make_lambda_code(function_decl), expected_lambda_code_buffer )

    test_with_two_template_buffers()


    def test_with_variadic_fmt():
        function_decl = """
            MY_API void TagX(double x, const ImVec4& color, const char* fmt, ...)           IM_FMTARGS(3);
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
            MY_API inline void add_inside_array(int8_t* array, int array_size, int number_to_add);
        """

        expected_lambda_code_buffer = """
            [](py::array & array, int number_to_add)
            {
                // convert array (py::array&) to C standard buffer (mutable)
                void* array_buffer = array.mutable_data();
                int array_count = array.shape()[0];
            
                char array_type = array.dtype().char_();
                if (array_type != 'b')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a buffer of native type:
                                        int8_t*
                                    Which is equivalent to
                                        b
                                    (using py::array::dtype().char_() as an id)
                        )msg"));
                add_inside_array(static_cast<int8_t*>(array_buffer), array_count, number_to_add);
            },
        """

        options.buffer_flag_replace_by_array = True
        generated_code = make_lambda_code(function_decl)
        code_utils.assert_are_codes_equal( generated_code, expected_lambda_code_buffer )

    test_with_modifiable_int()
