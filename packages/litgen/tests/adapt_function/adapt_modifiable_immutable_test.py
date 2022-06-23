import logging

from codemanip import code_utils

import litgen


def test_modifiable_immutable_simple():
    options = litgen.LitgenOptions()
    code = "void foo(float * v);"
    generated_code = litgen.generate_code(options, code)

    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](BoxedFloat & v)
            {
                auto foo_adapt_modifiable_immutable = [](BoxedFloat & v)
                {
                    foo(& v.value);
                };

                foo_adapt_modifiable_immutable(v);
            },
            py::arg("v")
        );
    """,
    )

    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo(v: BoxedFloat) -> None:
            pass
    """,
    )


def test_modifiable_immutable_mixed_with_buffer():
    options = litgen.LitgenOptions()
    code = "void foo(float * buf, int buf_size);"
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo(buf: np.ndarray) -> None:
            pass
    """,
    )

    code = "void foo(float * buf, int buf_size, float *value, bool &flag);"
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo(buf: np.ndarray, value: BoxedFloat, flag: BoxedBool) -> None:
            pass
    """,
    )
