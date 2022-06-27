import logging

from codemanip import code_utils

import litgen


def test_modifiable_immutable_simple():
    options = litgen.LitgenOptions()
    options.fn_params_adapt_modifiable_immutable_regexes = [r".*"]
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
                    float * v_boxed_value = & (v.value);

                    foo(v_boxed_value);
                };

                foo_adapt_modifiable_immutable(v);
            },     py::arg("v"));
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

    code = "void foo(float * v = nullptr);"
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](BoxedFloat * v = nullptr)
            {
                auto foo_adapt_modifiable_immutable = [](BoxedFloat * v = nullptr)
                {
                    float * v_boxed_value = nullptr;
                    if (v != nullptr)
                        v_boxed_value = & (v->value);

                    foo(v_boxed_value);
                };

                foo_adapt_modifiable_immutable(v);
            },     py::arg("v") = py::none());
        """,
    )

    code = "int foo(float & v);"
    generated_code = litgen.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo",
            [](BoxedFloat & v) -> int
            {
                auto foo_adapt_modifiable_immutable = [](BoxedFloat & v) -> int
                {
                    float & v_boxed_value = v.value;

                    auto r = foo(v_boxed_value);
                    return r;
                };

                return foo_adapt_modifiable_immutable(v);
            },     py::arg("v"));
        """,
    )


def test_modifiable_immutable_mixed_with_buffer():
    options = litgen.LitgenOptions()
    options.fn_params_adapt_modifiable_immutable_regexes = [r".*"]
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
