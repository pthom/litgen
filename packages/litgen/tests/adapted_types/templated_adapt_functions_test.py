from codemanip import code_utils

import litgen


def test_templated_function():
    code = """
        struct Foo
        {
            template<typename T>
            MY_API T SumVector(std::vector<T> xs, const T other_values[2]);
        };
        """
    options = litgen.LitgenOptions()
    options.fn_template_options[r"SumVector"] = ["int"]
    options.fn_params_replace_buffer_by_array__regex = r".*"

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class Foo:
            def sum_vector(self, xs: List[int], other_values: List[int]) -> MY_API int:
                pass
    """,
    )
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            .def("sum_vector",
                [](Foo & self, std::vector<int> xs, const std::array<int, 2>& other_values) -> MY_API int
                {
                    auto SumVector_adapt_fixed_size_c_arrays = [&self](std::vector<int> xs, const std::array<int, 2>& other_values) -> MY_API int
                    {
                        auto r = self.SumVector<int>(xs, other_values.data());
                        return r;
                    };

                    return SumVector_adapt_fixed_size_c_arrays(xs, other_values);
                },     py::arg("xs"), py::arg("other_values"))
            ;
    """,
    )
