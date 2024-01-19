from __future__ import annotations
from codemanip import code_utils

import litgen


def test_exclude_params():
    options = litgen.LitgenOptions()

    code = "void foo(int a, bool flag1, MyCallback callback = nullptr, bool flag2 = true);"
    options.fn_params_exclude_types__regex = "Callback$"
    options.fn_params_exclude_names__regex = "^flag"

    generated_code = litgen.generate_code(options, code)
    # logging. warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](int a, bool flag1)
            {
                auto foo_adapt_exclude_params = [](int a, bool flag1)
                {
                    foo(a, flag1, nullptr, true);
                };

                foo_adapt_exclude_params(a, flag1);
            },     py::arg("a"), py::arg("flag1"));
    """,
    )

    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo(a: int, flag1: bool) -> None:
            pass
    """,
    )
