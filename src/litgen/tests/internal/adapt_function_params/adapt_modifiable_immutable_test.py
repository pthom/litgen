from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen import litgen_generator


def test_modifiable_immutable_simple():
    options = litgen.LitgenOptions()
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = r".*"
    code = "void foo(float * v);"
    generated_code = litgen_generator.generate_code(options, code)

    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        ////////////////////    <generated_from:BoxedTypes>    ////////////////////
        auto pyClassBoxedFloat =
            py::class_<BoxedFloat>
                (m, "BoxedFloat", "")
            .def_readwrite("value", &BoxedFloat::value, "")
            .def(py::init<float>(),
                py::arg("v") = 0.)
            .def("__repr__",
                &BoxedFloat::__repr__)
            ;
        ////////////////////    </generated_from:BoxedTypes>    ////////////////////


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
        ####################    <generated_from:BoxedTypes>    ####################
        class BoxedFloat:
            value: float
            def __init__(self, v: float = 0.) -> None:
                pass
            def __repr__(self) -> str:
                pass
        ####################    </generated_from:BoxedTypes>    ####################


        def foo(v: BoxedFloat) -> None:
            pass
    """,
    )

    code = "void foo(float * v = nullptr);"
    generated_code = litgen_generator.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        ////////////////////    <generated_from:BoxedTypes>    ////////////////////
        auto pyClassBoxedFloat =
            py::class_<BoxedFloat>
                (m, "BoxedFloat", "")
            .def_readwrite("value", &BoxedFloat::value, "")
            .def(py::init<float>(),
                py::arg("v") = 0.)
            .def("__repr__",
                &BoxedFloat::__repr__)
            ;
        ////////////////////    </generated_from:BoxedTypes>    ////////////////////


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
    generated_code = litgen_generator.generate_code(options, code)
    # logging.warning("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        ////////////////////    <generated_from:BoxedTypes>    ////////////////////
        auto pyClassBoxedFloat =
            py::class_<BoxedFloat>
                (m, "BoxedFloat", "")
            .def_readwrite("value", &BoxedFloat::value, "")
            .def(py::init<float>(),
                py::arg("v") = 0.)
            .def("__repr__",
                &BoxedFloat::__repr__)
            ;
        ////////////////////    </generated_from:BoxedTypes>    ////////////////////


        m.def("foo",
            [](BoxedFloat & v) -> int
            {
                auto foo_adapt_modifiable_immutable = [](BoxedFloat & v) -> int
                {
                    float & v_boxed_value = v.value;

                    auto lambda_result = foo(v_boxed_value);
                    return lambda_result;
                };

                return foo_adapt_modifiable_immutable(v);
            },     py::arg("v"));
        """,
    )


def test_modifiable_immutable_mixed_with_buffer():
    options = litgen.LitgenOptions()
    options.fn_params_replace_buffer_by_array__regex = r".*"
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = r".*"
    code = "void foo(float * buf, int buf_size);"
    generated_code = litgen_generator.generate_code(options, code)
    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo(buf: np.ndarray) -> None:
            pass
    """,
    )

    code = "void foo(float * buf, int buf_size, float *value, bool &flag);"
    generated_code = litgen_generator.generate_code(options, code)
    # logging.warning("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        ####################    <generated_from:BoxedTypes>    ####################
        class BoxedBool:
            value: bool
            def __init__(self, v: bool = False) -> None:
                pass
            def __repr__(self) -> str:
                pass
        class BoxedFloat:
            value: float
            def __init__(self, v: float = 0.) -> None:
                pass
            def __repr__(self) -> str:
                pass
        ####################    </generated_from:BoxedTypes>    ####################


        def foo(buf: np.ndarray, value: BoxedFloat, flag: BoxedBool) -> None:
            pass
            """,
    )
