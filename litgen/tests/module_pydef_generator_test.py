import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

from litgen.internal import module_pydef_generator, code_utils
from litgen.internal import srcml
from litgen import CodeStyleOptions, code_style_implot, code_style_immvision


#################################
#           Enums
################################

def test_generate_pydef_enum():
    options = code_style_implot()

    code1 = """
        // This is the enum doc
        enum MyEnum {
            // A doc on several values 
            MyEnum_A = 0, // Doc about A
            MyEnum_B,     // Doc about B
            // Count the number of values in the enum
            MyEnum_COUNT
        };        
    """

    expected_generated_code1 = """
        py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(),
            "This is the enum doc")
            // A doc on several values
            .value("a", MyEnum_A, "(Doc about A)")
            .value("b", MyEnum_B, "(Doc about B)")
        ;
    """

    cpp_unit1 = srcml.code_to_cpp_unit(options, code1)
    generated_code1 = module_pydef_generator.generate_pydef(cpp_unit1, options)
    code_utils.assert_are_codes_equal(expected_generated_code1, generated_code1)

    code2 = """
        // This is the enum doc
        enum class MyEnum {
            // A doc on several values
            A = 0, // Doc about A
            B,     // Doc about B
            // Count the number of values in the enum
            COUNT
        };
    """
    expected_generated_code2 = """
        py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(),
            "This is the enum doc")
            // A doc on several values
            .value("a", MyEnum::A, "(Doc about A)")
            .value("b", MyEnum::B, "(Doc about B)")
        ;
    """
    cpp_unit2 = srcml.code_to_cpp_unit(options, code2)
    generated_code2 = module_pydef_generator.generate_pydef(cpp_unit2, options)
    code_utils.assert_are_codes_equal(expected_generated_code2, generated_code2)


#################################
#           Functions
################################


def test_generate_pydef_function_cpp_code() -> str:

    def test_implot_easy():
        options = code_style_implot()
        code = '''
            // Sets the format of numeric axis labels
            IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
        '''
        cpp_unit = srcml.code_to_cpp_unit(options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("setup_axis_format",
                [](ImAxis axis, const char * fmt)
                {
                    { SetupAxisFormat(axis, fmt); return; }
                },
                py::arg("axis"),
                py::arg("fmt"),
                "Sets the format of numeric axis labels"
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_easy()

    def test_implot_one_buffer():
        options = code_style_implot()
        code = '''
            // Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.
            IMPLOT_TMP void PlotScatter(const T* values, int count);
        '''
        cpp_unit = srcml.code_to_cpp_unit(options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("plot_scatter",
                [](const py::array & values)
                {
                    // convert values (py::array&) to C standard buffer (const)
                    const void* values_buffer = values.data();
                    int values_count = values.shape()[0];

                    char array_type = values.dtype().char_();
                    if (array_type == 'B')
                        { PlotScatter(static_cast<const uint8_t*>(values_buffer), values_count); return; }
                    if (array_type == 'b')
                        { PlotScatter(static_cast<const int8_t*>(values_buffer), values_count); return; }
                    if (array_type == 'H')
                        { PlotScatter(static_cast<const uint16_t*>(values_buffer), values_count); return; }
                    if (array_type == 'h')
                        { PlotScatter(static_cast<const int16_t*>(values_buffer), values_count); return; }
                    if (array_type == 'I')
                        { PlotScatter(static_cast<const uint32_t*>(values_buffer), values_count); return; }
                    if (array_type == 'i')
                        { PlotScatter(static_cast<const int32_t*>(values_buffer), values_count); return; }
                    if (array_type == 'L')
                        { PlotScatter(static_cast<const uint64_t*>(values_buffer), values_count); return; }
                    if (array_type == 'l')
                        { PlotScatter(static_cast<const int64_t*>(values_buffer), values_count); return; }
                    if (array_type == 'f')
                        { PlotScatter(static_cast<const float*>(values_buffer), values_count); return; }
                    if (array_type == 'd')
                        { PlotScatter(static_cast<const double*>(values_buffer), values_count); return; }
                    if (array_type == 'g')
                        { PlotScatter(static_cast<const long double*>(values_buffer), values_count); return; }

                    // If we arrive here, the array type is not supported!
                    throw std::runtime_error(std::string("Bad array type: ") + array_type );
                },
                py::arg("values"),
                "Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle."
            );
       '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_one_buffer()

    def test_immvision():
        options = code_style_immvision()
        code = """
            // Display an image (requires OpenGL initialized)
            IMMVISION_API bool Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);
        """
        cpp_unit = srcml.code_to_cpp_unit(options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("image",
                [](const std::string & label_id, const cv::Mat & mat, ImageParams * params)
                {
                    { return Image(label_id, mat, params); }
                },
                py::arg("label_id"),
                py::arg("mat"),
                py::arg("params"),
                "Display an image (requires OpenGL initialized)"
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_immvision()



"""
test_generate_python_wrapper_init_code will need to be handled later (or not !)
"""
# def test_generate_python_wrapper_init_code():
# def test_simple():
#     code = """
#     // Adds two numbers
#     IMMVISION_API int add(int a, int b);
#     """
#     options = code_style_immvision()
#     cpp_unit = srcml.srcml_main.code_to_cpp_unit(options, code)
#     generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
#     expected_code = '''
#         def add(
#             a: int,
#             b: int):
#             """Adds two numbers
#             """
#             r = _cpp_immvision.add(a, b)
#             return r
#         '''
#     # logging.warning("\n" + generated_code)
#     code_utils.assert_are_codes_equal(generated_code, expected_code)
#
# test_simple()

#     def test_require_opengl():
#         code = """
#         // Display an image, with full user control: zoom, pan, watch pixels, etc.
#         // requires OpenGL initialized.
#         IMMVISION_API void Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);
#         """
#         options = code_style_immvision()
#         function_infos = function_parser.parse_one_function_declaration(code, options)
#         generated_code = function_generator.generate_python_wrapper_init_code(function_infos, options)
#         expected_code = '''
#             def image(
#                 label_id:  str,
#                 mat:  np.ndarray,
#                 params: ImageParams):
#                 """Display an image, with full user control: zoom, pan, watch pixels, etc.
#                 requires OpenGL initialized.
#                 """
#
#                 _cpp_immvision.transfer_imgui_context_python_to_cpp()
#
#                 r = _cpp_immvision.image(label_id, mat, params)
#                 return r
#         '''
#
#         code_utils.assert_are_codes_equal(generated_code, expected_code)
#
#     test_require_opengl()


