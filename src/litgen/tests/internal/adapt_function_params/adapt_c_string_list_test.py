from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen.litgen_generator import LitgenGeneratorTestsHelper


def to_pydef(code: str) -> str:
    options = litgen.LitgenOptions()
    options.fn_params_replace_c_string_list__regex = r".*"
    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    return pydef_code


def test_c_string_list_simple():
    code = "void foo(const char * const items[], int items_count);"
    generated_code = to_pydef(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        m.def("foo",
            [](const std::vector<std::string> & items)
            {
                auto foo_adapt_c_string_list = [](const std::vector<std::string> & items)
                {
                    std::vector<const char *> items_ptrs;
                    for (const auto& v: items)
                        items_ptrs.push_back(v.c_str());
                    int items_count = static_cast<int>(items.size());

                    foo(items_ptrs.data(), items_count);
                };

                foo_adapt_c_string_list(items);
            },     py::arg("items"));
        """,
    )


def test_mix_array_and_string_list():
    code = "int foo(const char * const items[], int items_count, int ouput[2]);"
    generated_code = to_pydef(code)
    # logging. warning("\n" + generated_code)
    code_utils.assert_are_codes_equal(
        generated_code,
        """
        ////////////////////    <generated_from:BoxedTypes>    ////////////////////
        auto pyClassBoxedInt =
            py::class_<BoxedInt>
                (m, "BoxedInt", "")
            .def_readwrite("value", &BoxedInt::value, "")
            .def(py::init<int>(),
                py::arg("v") = 0)
            .def("__repr__",
                &BoxedInt::__repr__)
            ;
        ////////////////////    </generated_from:BoxedTypes>    ////////////////////


        m.def("foo",
            [](const std::vector<std::string> & items, BoxedInt & ouput_0, BoxedInt & ouput_1) -> int
            {
                auto foo_adapt_fixed_size_c_arrays = [](const char * const items[], int items_count, BoxedInt & ouput_0, BoxedInt & ouput_1) -> int
                {
                    int ouput_raw[2];
                    ouput_raw[0] = ouput_0.value;
                    ouput_raw[1] = ouput_1.value;

                    auto lambda_result = foo(items, items_count, ouput_raw);

                    ouput_0.value = ouput_raw[0];
                    ouput_1.value = ouput_raw[1];
                    return lambda_result;
                };
                auto foo_adapt_c_string_list = [&foo_adapt_fixed_size_c_arrays](const std::vector<std::string> & items, BoxedInt & ouput_0, BoxedInt & ouput_1) -> int
                {
                    std::vector<const char *> items_ptrs;
                    for (const auto& v: items)
                        items_ptrs.push_back(v.c_str());
                    int items_count = static_cast<int>(items.size());

                    auto lambda_result = foo_adapt_fixed_size_c_arrays(items_ptrs.data(), items_count, ouput_0, ouput_1);
                    return lambda_result;
                };

                return foo_adapt_c_string_list(items, ouput_0, ouput_1);
            },     py::arg("items"), py::arg("ouput_0"), py::arg("ouput_1"));
        """,
    )
