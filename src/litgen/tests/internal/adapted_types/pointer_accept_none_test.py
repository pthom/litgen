from __future__ import annotations
from codemanip import code_utils

import litgen

CODE = """
void SetCurrentContext(Context* ctx);
void SetOther(Context* ctx);
struct Editor
{
    void SetLanguage(const Language* language);
};
"""

EXPECTED_STUB = """
def set_current_context(ctx: Optional[Context]) -> None:
    pass
def set_other(ctx: Context) -> None:
    pass
class Editor:
    def set_language(self, language: Optional[Language]) -> None:
        pass
    def __init__(self) -> None:
        \"\"\"Auto-generated default constructor\"\"\"
        pass
"""


def test_pointer_accept_none_nanobind():
    options = litgen.LitgenOptions()
    options.use_nanobind()
    options.fn_params_pointer_accept_none__regex = r"^Set(CurrentContext|Language)$"
    generated_code = litgen.generate_code(options, CODE)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("set_current_context",
            SetCurrentContext, nb::arg("ctx").none());

        m.def("set_other",
            SetOther, nb::arg("ctx"));


        auto pyClassEditor =
            nb::class_<Editor>
                (m, "Editor", "")
            .def(nb::init<>()) // implicit default constructor
            .def("set_language",
                &Editor::SetLanguage, nb::arg("language").none())
            ;
        """,
    )
    code_utils.assert_are_codes_equal(generated_code.stub_code, EXPECTED_STUB)


def test_pointer_accept_none_pybind():
    # pybind11 accepts None for pointer params: only the stub changes
    options = litgen.LitgenOptions()
    options.fn_params_pointer_accept_none__regex = r"^Set(CurrentContext|Language)$"
    generated_code = litgen.generate_code(options, CODE)
    assert ".none()" not in generated_code.pydef_code
    code_utils.assert_are_codes_equal(generated_code.stub_code, EXPECTED_STUB)
