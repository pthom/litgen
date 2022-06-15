import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")

from litgen.internal import module_pydef_generator, code_utils
import srcmlcpp
from litgen import CodeStyleOptions
from litgen.options import code_style_implot, code_style_immvision


#################################
#           Enums
################################

def test_generate_pydef_enum():
    options = code_style_implot()

    code1 = """
        // This is the enum doc
        // on two lines
        enum MyEnum {
            // A doc on several values 
            // on several lines
            MyEnum_A = 0, // Doc about A
            MyEnum_B,     
            // Count the number of values in the enum
            MyEnum_COUNT
        };        
    """

    expected_generated_code1 = """py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(), " This is the enum doc\\n on two lines")
    //  A doc on several values
    //  on several lines
    .value("a", MyEnum_A, " Doc about A")
    .value("b", MyEnum_B, "");
    """

    cpp_unit1 = srcmlcpp.code_to_cpp_unit(options.srcml_options, code1)
    generated_code1 = module_pydef_generator.generate_pydef(cpp_unit1, options)
    # logging.warning("\n" + generated_code1)
    code_utils.assert_are_codes_equal(generated_code1, expected_generated_code1)

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
    expected_generated_code2 = """py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(), " This is the enum doc")
    //  A doc on several values
    .value("a", MyEnum::A, " Doc about A")
    .value("b", MyEnum::B, " Doc about B");
    """
    cpp_unit2 = srcmlcpp.code_to_cpp_unit(options.srcml_options, code2)
    generated_code2 = module_pydef_generator.generate_pydef(cpp_unit2, options)
    code_utils.assert_are_codes_equal(generated_code2, expected_generated_code2)


#################################
#           Functions
################################


def test_generate_pydef_function_cpp_code() -> str:

    def test_implot_easy():
        options = code_style_implot()
        code = '''
            // Sets the format of numeric 
            // axis labels
            IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
        '''
        cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
        m.def("setup_axis_format",
            [](ImAxis axis, const char * fmt)
            {
                SetupAxisFormat(axis, fmt);
            },
            py::arg("axis"), py::arg("fmt"),
            " Sets the format of numeric \\n axis labels"
        );
        '''
        # logging.warning("\n" + generated_code)
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_implot_easy()

    def test_return_value_policy():
        options = code_style_implot()
        code = '''
            // Returns a widget
            IMPLOT_API Widget* Foo();  // return_value_policy::reference
        '''
        cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("foo",
                []()
                {
                    return Foo();
                },
                " Returns a widget\\n\\n return_value_policy::reference",
                pybind11::return_value_policy::reference
            );
        '''
        code_utils.assert_are_codes_equal(generated_code, expected_code)

    test_return_value_policy()

    def test_implot_one_buffer():
        options = code_style_implot()
        code = '''
            // Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.
            IMPLOT_TMP void PlotScatter(const T* values, int count);
        '''
        cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("plot_scatter",
                [](const py::array & values)
                {
                    auto PlotScatter_adapt_c_buffers = [](const py::array & values)
                    {
                        // convert py::array to C standard buffer (const)
                        const void * values_from_pyarray = values.data();
                        py::ssize_t values_count = values.shape()[0];
            
                        // call the correct template version by casting
                        char values_type = values.dtype().char_();
                        if (values_type == 'B')
                            PlotScatter(static_cast<const uint8_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'b')
                            PlotScatter(static_cast<const int8_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'H')
                            PlotScatter(static_cast<const uint16_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'h')
                            PlotScatter(static_cast<const int16_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'I')
                            PlotScatter(static_cast<const uint32_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'i')
                            PlotScatter(static_cast<const int32_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'L')
                            PlotScatter(static_cast<const uint64_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'l')
                            PlotScatter(static_cast<const int64_t *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'f')
                            PlotScatter(static_cast<const float *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'd')
                            PlotScatter(static_cast<const double *>(values_from_pyarray), static_cast<int>(values_count));
                        else if (values_type == 'g')
                            PlotScatter(static_cast<const long double *>(values_from_pyarray), static_cast<int>(values_count));
                        // If we reach this point, the array type is not supported!
                        else
                            throw std::runtime_error(std::string("Bad array type ('") + values_type + "') for param values");
                    };
            
                    PlotScatter_adapt_c_buffers(values);
                },
                py::arg("values"),
                " Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle."
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
        cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
        generated_code = module_pydef_generator.generate_pydef(cpp_unit, options)
        expected_code = '''
            m.def("image",
                [](const std::string & label_id, const cv::Mat & mat, ImageParams * params)
                {
                    return Image(label_id, mat, params);
                },
                py::arg("label_id"), py::arg("mat"), py::arg("params"),
                " Display an image (requires OpenGL initialized)"
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
#     cpp_unit = srcmlcpp.srcml_main.code_to_cpp_unit(options, code)
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


#################################
#           Structs
################################


def test_generate_pydef_struct_cpp_code():
    options = code_style_immvision()
    code = """
        // A dummy structure that likes to multiply
        struct Multiplier 
        { 
            Multiplier(); // default constructor
            
            // Constructor with param
            Multiplier(int _who): who(_who) {}; 
            
            // Doubles the input number
            IMMVISION_API int CalculateDouble(int x = 21) 
            { 
                return x * 2; 
            }
            // Who is who?
            int who = 627;
        };
    """
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    generated = module_pydef_generator.generate_pydef(cpp_unit, options)
    expected_code = """


        auto pyClassMultiplier = py::class_<Multiplier>
            (m, "Multiplier", " A dummy structure that likes to multiply")
            .def(py::init<>(),
                " default constructor")
            .def(py::init<int>(),
                py::arg("_who"),
                " Constructor with param")
            .def("calculate_double",
                [](Multiplier & self, int x = 21)
                {
                    return self.CalculateDouble(x);
                },
                py::arg("x") = 21,
                " Doubles the input number"
            )
            .def_readwrite("who", &Multiplier::who, " Who is who?")
            .def("__repr__", [](const Multiplier& v) { return ToString(v); });
    """
    # logging.warning("\n" + generated)
    code_utils.assert_are_codes_equal(generated, expected_code)
