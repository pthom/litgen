from __future__ import annotations
from codemanip import code_utils

import litgen


def test_text_end_params():
    options = litgen.LitgenOptions()
    options.fn_params_text_end_names__regex = r"_end$"

    code = """
    void SeparatorTextEx(const char* label, const char* label_end, float extra_width);
    void TextUnformatted(const char* text, const char* text_end = NULL);
    void Other(int count_end, const char* name);
    """

    generated_code = litgen.generate_code(options, code)
    # logging. warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("separator_text_ex",
            [](const char * label, float extra_width)
            {
                auto SeparatorTextEx_adapt_text_end_params = [](const char * label, float extra_width)
                {
                    SeparatorTextEx(label, label ? label + strlen(label) : nullptr, extra_width);
                };

                SeparatorTextEx_adapt_text_end_params(label, extra_width);
            },     py::arg("label"), py::arg("extra_width"));

        m.def("text_unformatted",
            [](const char * text)
            {
                auto TextUnformatted_adapt_text_end_params = [](const char * text)
                {
                    TextUnformatted(text, NULL);
                };

                TextUnformatted_adapt_text_end_params(text);
            },     py::arg("text"));

        m.def("other",
            Other, py::arg("count_end"), py::arg("name"));
    """,
    )

    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def separator_text_ex(label: str, extra_width: float) -> None:
            pass
        def text_unformatted(text: str) -> None:
            pass
        def other(count_end: int, name: str) -> None:
            pass
    """,
    )


def test_text_end_params_off_by_default():
    options = litgen.LitgenOptions()
    code = "void TextUnformatted(const char* text, const char* text_end = NULL);"
    generated_code = litgen.generate_code(options, code)
    assert "text_end" in generated_code.stub_code
