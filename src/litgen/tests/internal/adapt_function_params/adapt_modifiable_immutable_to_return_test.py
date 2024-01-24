from __future__ import annotations
from codemanip import code_utils

import litgen


def test_adapt_modifiable_immutable_to_return_test():
    options = litgen.LitgenOptions()
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"

    code = """
    MY_API bool SliderBoolInt(const char* label, int * value);
    MY_API void SliderVoidInt(const char* label, int * value);
    MY_API bool SliderBoolInt2(const char* label, int * value1, int * value2);
    MY_API bool SliderVoidIntDefaultNull(const char* label, int * value = nullptr);
    """

    generated_code = litgen.generate_code(options, code)

    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def slider_bool_int(label: str, value: int) -> Tuple[bool, int]:
            pass
        def slider_void_int(label: str, value: int) -> int:
            pass
        def slider_bool_int2(label: str, value1: int, value2: int) -> Tuple[bool, int, int]:
            pass
        def slider_void_int_default_null(
            label: str,
            value: Optional[int] = None
            ) -> Tuple[bool, Optional[int]]:
            pass
        """,
    )

    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("slider_bool_int",
            [](const char * label, int value) -> std::tuple<bool, int>
            {
                auto SliderBoolInt_adapt_modifiable_immutable_to_return = [](const char * label, int value) -> std::tuple<bool, int>
                {
                    int * value_adapt_modifiable = & value;

                    bool r = SliderBoolInt(label, value_adapt_modifiable);
                    return std::make_tuple(r, value);
                };

                return SliderBoolInt_adapt_modifiable_immutable_to_return(label, value);
            },     py::arg("label"), py::arg("value"));

        m.def("slider_void_int",
            [](const char * label, int value) -> int
            {
                auto SliderVoidInt_adapt_modifiable_immutable_to_return = [](const char * label, int value) -> int
                {
                    int * value_adapt_modifiable = & value;

                    SliderVoidInt(label, value_adapt_modifiable);
                    return value;
                };

                return SliderVoidInt_adapt_modifiable_immutable_to_return(label, value);
            },     py::arg("label"), py::arg("value"));

        m.def("slider_bool_int2",
            [](const char * label, int value1, int value2) -> std::tuple<bool, int, int>
            {
                auto SliderBoolInt2_adapt_modifiable_immutable_to_return = [](const char * label, int value1, int value2) -> std::tuple<bool, int, int>
                {
                    int * value1_adapt_modifiable = & value1;
                    int * value2_adapt_modifiable = & value2;

                    bool r = SliderBoolInt2(label, value1_adapt_modifiable, value2_adapt_modifiable);
                    return std::make_tuple(r, value1, value2);
                };

                return SliderBoolInt2_adapt_modifiable_immutable_to_return(label, value1, value2);
            },     py::arg("label"), py::arg("value1"), py::arg("value2"));

        m.def("slider_void_int_default_null",
            [](const char * label, std::optional<int> value = std::nullopt) -> std::tuple<bool, std::optional<int>>
            {
                auto SliderVoidIntDefaultNull_adapt_modifiable_immutable_to_return = [](const char * label, std::optional<int> value = std::nullopt) -> std::tuple<bool, std::optional<int>>
                {
                    int * value_adapt_modifiable = nullptr;
                    if (value.has_value())
                        value_adapt_modifiable = & (*value);

                    bool r = SliderVoidIntDefaultNull(label, value_adapt_modifiable);
                    return std::make_tuple(r, value);
                };

                return SliderVoidIntDefaultNull_adapt_modifiable_immutable_to_return(label, value);
            },     py::arg("label"), py::arg("value") = py::none());
    """,
    )


def test_adapt_modifiable_immutable_to_return_array():
    options = litgen.LitgenOptions()
    options.fn_params_replace_c_array_modifiable_by_boxed__regex = ""
    options.fn_params_output_modifiable_immutable_to_return__regex = r".*"
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    code = "MY_API bool SliderVoidIntArray(const char* label, int value[3]);"
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("slider_void_int_array",
            [](const char * label, std::array<int, 3> value) -> std::tuple<bool, std::array<int, 3>>
            {
                auto SliderVoidIntArray_adapt_modifiable_immutable_to_return = [](const char * label, std::array<int, 3> value) -> std::tuple<bool, std::array<int, 3>>
                {
                    int * value_adapt_modifiable = value.data();

                    bool r = SliderVoidIntArray(label, value_adapt_modifiable);
                    return std::make_tuple(r, value);
                };

                return SliderVoidIntArray_adapt_modifiable_immutable_to_return(label, value);
            },     py::arg("label"), py::arg("value"));
    """,
    )
    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def slider_void_int_array(label: str, value: List[int]) -> Tuple[bool, List[int]]:
            pass
    """,
    )
