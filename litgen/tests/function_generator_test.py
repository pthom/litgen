import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import code_utils
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot
import function_generator, function_parser


def test_generate_python_wrapper_init_code():
    def test_simple():
        code = """
        // Adds two numbers
        IMMVISION_API int add(int a, int b);    
        """
        options = code_style_immvision()
        function_infos = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_python_wrapper_init_code(function_infos, options)
        expected_code = '''
            def add(
                a: int,
                b: int):
                """Adds two numbers
                """
                r = _cpp_immvision.add(a, b)
                return r
            '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_simple()

    def test_require_opengl():
        code = """
        // Display an image, with full user control: zoom, pan, watch pixels, etc.
        // requires OpenGL initialized.
        IMMVISION_API void Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);
        """
        options = code_style_immvision()
        function_infos = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_python_wrapper_init_code(function_infos, options)
        expected_code = '''
            def image(
                label_id:  str,
                mat:  np.ndarray,
                params: ImageParams):
                """Display an image, with full user control: zoom, pan, watch pixels, etc.
                requires OpenGL initialized.
                """
            
                _cpp_immvision.transfer_imgui_context_python_to_cpp()
            
                r = _cpp_immvision.image(label_id, mat, params)
                return r
        '''

        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_require_opengl()


def test_generate_pydef_function_cpp_code() -> str:

    def test_implot_easy():
        options = code_style_implot()
        code = '''
            // Sets the format of numeric axis labels
            IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
        '''
        function_info = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
        expected_code = '''
            m.def("setup_axis_format",
                [](ImAxis axis, const char* fmt)
                {
                     SetupAxisFormat(axis, fmt);
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
        function_info = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
        expected_code = '''
            m.def("plot_scatter",
                [](const py::array & values)
                {
                    // convert values (py::array&) to C standard buffer
                    void* values_buffer = (void*) values.data();
                    int values_count = values.shape()[0];
            
                     PlotScatter(values_buffer, values_count);
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
        function_info = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
        expected_code = '''
            m.def("image",
                [](const std::string& label_id, const cv::Mat& mat, ImageParams* params)
                {
                    return Image(label_id, mat, params);
                },
                py::arg("label_id"),
                py::arg("mat"),
                py::arg("params"),
                "Display an image (requires OpenGL initialized)"
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_immvision()
