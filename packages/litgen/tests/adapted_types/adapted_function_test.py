from srcmlcpp import srcml_main
from srcmlcpp.srcml_types import *

import litgen
from litgen.internal.adapted_types import *
from litgen.options import code_style_implot, code_style_immvision


def test_adapted_function_stub():
    options = litgen.LitgenOptions()
    options.original_location_flag_show = True

    code = """
    // This is foo's doc:
    //     :param buffer & count: modifiable buffer and its size
    //     :param out_values: output double values
    //     :param in_flags: input bool flags
    //     :param text and ... : formatted text
    void Foo(uint8_t * buffer, size_t count, double out_values[2], const bool in_flags[2], const char* text, ...);
    """
    stub_code = litgen.code_to_stub(options, code)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        def foo(    # Line:7
            buffer: np.ndarray,
            out_values_0: BoxedDouble,
            out_values_1: BoxedDouble,
            in_flags: List[bool],
            text: str
            ) -> None:
            """ This is foo's doc:
                 :param buffer  count: modifiable buffer and its size
                 :param out_values: output float values
                 :param in_flags: input bool flags
                 :param text and ... : formatted text
            """
            pass
    ''',
    )


def test_adapted_function_pydef_simple():
    options = litgen.LitgenOptions()
    code = """
    int add(int a, int b) { return a + b; }
    """
    pydef_code = litgen.code_to_pydef(options, code)
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("add",
            [](int a, int b)
            {
                return add(a, b);
            },
            py::arg("a"), py::arg("b")
        );
    """,
    )


def test_implot_easy() -> None:
    options = code_style_implot()
    code = """
        // Sets the format of numeric
        // axis labels
        IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
    """
    generated_code = litgen.code_to_pydef(options, code)
    expected_code = """
    m.def("setup_axis_format",
        [](ImAxis axis, const char * fmt)
        {
            SetupAxisFormat(axis, fmt);
        },
        py::arg("axis"), py::arg("fmt"),
        " Sets the format of numeric\\n axis labels"
    );
    """
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_return_value_policy() -> None:
    options = code_style_implot()
    code = """
        // Returns a widget
        IMPLOT_API Widget* Foo();  // return_value_policy::reference
    """
    generated_code = litgen.code_to_pydef(options, code)
    expected_code = """
        m.def("foo",
            []()
            {
                return Foo();
            },
            " Returns a widget\\n\\n return_value_policy::reference",
            pybind11::return_value_policy::reference
        );
    """
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_implot_one_buffer() -> None:
    options = code_style_implot()
    code = """
        // Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.
        IMPLOT_TMP void PlotScatter(const T* values, int count);
    """
    generated_code = litgen.code_to_pydef(options, code)
    expected_code = """
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
            "Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle."
        );
   """
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_immvision() -> None:
    options = code_style_immvision()
    code = """
        // Display an image (requires OpenGL initialized)
        IMMVISION_API bool Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);
    """
    generated_code = litgen.code_to_pydef(options, code)
    expected_code = """
        m.def("image",
            [](const std::string & label_id, const cv::Mat & mat, ImageParams * params)
            {
                return Image(label_id, mat, params);
            },
            py::arg("label_id"), py::arg("mat"), py::arg("params"),
            "Display an image (requires OpenGL initialized)"
        );
    """
    code_utils.assert_are_codes_equal(generated_code, expected_code)
