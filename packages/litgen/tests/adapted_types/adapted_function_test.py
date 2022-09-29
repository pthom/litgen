from srcmlcpp.srcml_types import *

from litgen.options import LitgenOptions
from litgen.litgen_generator import LitgenGeneratorTestsHelper


def test_adapted_function_stub():
    options = LitgenOptions()
    options.original_location_flag_show = True
    options.fn_params_replace_buffer_by_array__regex = r".*"

    code = """
    // This is foo's doc:
    //     :param buffer & count: modifiable buffer and its size
    //     :param out_values: output double values
    //     :param in_flags: input bool flags
    //     :param text and ... : formatted text
    void Foo(uint8_t * buffer, size_t count, double out_values[2], const bool in_flags[2], const char* text, ...);
    """
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        ####################    <generated_from:BoxedTypes>    ####################
        class BoxedDouble:
            value: float
            def __init__(self, v: float = 0.) -> None:
                pass
            def __repr__(self) -> str:
                pass
        ####################    </generated_from:BoxedTypes>    ####################



        def foo(    # Line:7
            buffer: np.ndarray,
            out_values_0: BoxedDouble,
            out_values_1: BoxedDouble,
            in_flags: List[bool],
            text: str
            ) -> None:
            """ This is foo's doc:
                 :param buffer & count: modifiable buffer and its size
                 :param out_values: output double values
                 :param in_flags: input bool flags
                 :param text and ... : formatted text
            """
            pass
            ''',
    )


def test_adapted_function_pydef_simple():
    options = LitgenOptions()
    code = """
    int add(int a, int b) { return a + b; }
    """
    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("add",
            add, py::arg("a"), py::arg("b"));
        """,
    )


def test_implot_easy() -> None:
    options = LitgenOptions()
    options.srcml_options.functions_api_prefixes = "IMPLOT_API|IMPLOT_TMP"
    options.original_location_flag_show = True
    code = """
        // Sets the format of numeric
        // axis labels
        IMPLOT_API void SetupAxisFormat(ImAxis axis, const char* fmt);
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    expected_code = """
        m.def("setup_axis_format",    // Line:4
            SetupAxisFormat,
            py::arg("axis"), py::arg("fmt"),
            " Sets the format of numeric\\n axis labels");
        """
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_return_value_policy() -> None:
    options = LitgenOptions()
    code = """
        // Returns a widget
        Widget* Foo();  // return_value_policy::reference
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + generated_code)
    expected_code = """
        m.def("foo",
            Foo,
            " Returns a widget\\nreturn_value_policy::reference",
            pybind11::return_value_policy::reference);
        """
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_implot_one_buffer() -> None:
    options = LitgenOptions()
    options.fn_params_replace_buffer_by_array__regex = r".*"
    options.srcml_options.functions_api_prefixes = "IMPLOT_API|IMPLOT_TMP"
    options.original_location_flag_show = True
    code = """
        // Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.
        IMPLOT_TMP void PlotScatter(const T* values, int count);
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    expected_code = """
        m.def("plot_scatter",    // Line:3
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
                    else if (values_type == 'q')
                        PlotScatter(static_cast<const long long *>(values_from_pyarray), static_cast<int>(values_count));
                    // If we reach this point, the array type is not supported!
                    else
                        throw std::runtime_error(std::string("Bad array type ('") + values_type + "') for param values");
                };

                PlotScatter_adapt_c_buffers(values);
            },
            py::arg("values"),
            "Plots a standard 2D scatter plot. Default marker is ImPlotMarker_Circle.");
   """
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_immvision() -> None:
    options = LitgenOptions()
    options.srcml_options.functions_api_prefixes = "IMMVISION_API"
    code = """
        // Display an image (requires OpenGL initialized)
        IMMVISION_API bool Image(const std::string& label_id, const cv::Mat& mat, ImageParams* params);
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    expected_code = """
        m.def("image",
            Image,
            py::arg("label_id"), py::arg("mat"), py::arg("params"),
            "Display an image (requires OpenGL initialized)");
        """
    code_utils.assert_are_codes_equal(generated_code, expected_code)


def test_overloads() -> None:
    options = LitgenOptions()
    code = """
    std::string foo();
    std::string foo(int a);
    void blah();
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            py::overload_cast<>(foo));

        m.def("foo",
            py::overload_cast<int>(foo), py::arg("a"));

        m.def("blah",
            blah);
        """,
    )

    code = """
    struct Foo
    {
        std::string foo();
        std::string foo(int a);
        void blah();
    };
    """
    generated_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        auto pyClassFoo = py::class_<Foo>
            (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            .def("foo",
                py::overload_cast<>(&Foo::foo))
            .def("foo",
                py::overload_cast<int>(&Foo::foo), py::arg("a"))
            .def("blah",
                &Foo::blah)
            ;
        """,
    )


def test_type_ignore():
    options = LitgenOptions()
    code = """
    // Foo doc
    std::string foo(); // type: ignore
    """
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # logging.warning("\n" + stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        """
    # Foo doc
    def foo() -> str:  # type: ignore
        pass
    """,
    )

    code = """
    std::string foo(); // type: ignore // Some more doc
    """
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # logging.warning("\n" + stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
    def foo() -> str:  # type: ignore
        """ Some more doc"""
        pass
    ''',
    )


def test_py_none_param():
    options = LitgenOptions()

    code = """
    void foo(Widget *a = nullptr);
    """
    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("foo",
            foo, py::arg("a") = py::none());
        """,
    )

    code = """
    void foo(Widget *a = NULL);
    """
    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("foo",
            foo, py::arg("a") = py::none());
        """,
    )

    code = """
    void foo(Widget *a = Widget(NULL));
    """
    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # logging.warning("\n" + pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        m.def("foo",
            foo, py::arg("a") = Widget(NULL));
        """,
    )
