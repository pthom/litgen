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
        //
        // :param mat
        //     An image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.
        //
        // - This function requires that both imgui and OpenGL were initialized.
        //   (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
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
        
            :param mat
            An image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.
        
            - This function requires that both imgui and OpenGL were initialized.
            (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
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
        // Sets the format of numeric axis labels via formater specifier (default="%g"). Formated values will be double (i.e. use %f).
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
        "Sets the format of numeric axis labels via formater specifier (default=\\"%g\\"). Formated values will be float (i.e. use %f)."
    );
                '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_easy()

    def test_implot_one_buffer():
        options = code_style_implot()
        code = '''
            // Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.
            IMPLOT_TMP void PlotScatter(const char* label_id, const T* values, int count, double xscale=1, double x0=0, int offset=0, int stride=sizeof(T));
        '''
        function_info = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
        expected_code = '''
            m.def("plot_scatter",
                [](const char* label_id, const py::array & values, double xscale = 1, double x0 = 0, int offset = 0, int stride = -1)
                {
                    // convert values (py::array&) to C standard buffer
                    const void* values_buffer = values.data();
                    int values_count = values.shape()[0];
                        
                    // process stride default value (which was a sizeof in C++)
                    int values_stride = stride;
                    if (values_stride == -1)
                        values_stride = (int)values.itemsize();
                        
                     PlotScatter(label_id, values_buffer, values_count, xscale, x0, offset, values_stride);
                },
                py::arg("label_id"),
                py::arg("values"),
                py::arg("xscale") = 1,
                py::arg("x0") = 0,
                py::arg("offset") = 0,
                py::arg("stride") = -1,
                "Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle."
            );        
    '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_one_buffer()

    def test_implot_two_buffers():
        options = code_style_implot()
        code = '''
            IMPLOT_TMP void PlotScatter(const char* label_id, const T* xs, const T* ys, int count, int offset=0, int stride=sizeof(T));
        '''
        function_info = function_parser.parse_one_function_declaration(code, options)
        generated_code = function_generator.generate_pydef_function_cpp_code(function_info, options)
        expected_code = '''
            m.def("plot_scatter",
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
                py::arg("label_id"),
                py::arg("xs"),
                py::arg("ys"),
                py::arg("offset") = 0,
                py::arg("stride") = -1,
                ""
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_two_buffers()

    def test_immvision():
        options = code_style_immvision()
        code = """
            // Display an image, with full user control: zoom, pan, watch pixels, etc.
            //
            // :param mat
            //     An image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.
            //
            // - This function requires that both imgui and OpenGL were initialized.
            //   (for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)
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
                "Display an image, with full user control: zoom, pan, watch pixels, etc.\\n\\n:param mat\\nAn image you want to display, under the form of an OpenCV matrix. All types of dense matrices are supported.\\n\\n- This function requires that both imgui and OpenGL were initialized.\\n(for example, use `imgui_runner.run`for Python,  or `HelloImGui::Run` for C++)"
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_immvision()
