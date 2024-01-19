from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen.internal import boxed_python_type
from litgen.litgen_generator import LitgenGenerator


def test_boxed_type_cpp_struct_code():
    options = litgen.LitgenOptions()
    code = boxed_python_type.boxed_type_cpp_struct_code("std::string", options._indent_cpp_spaces())
    code_utils.assert_are_codes_equal(
        code,
        """
        struct BoxedString
        {
            std::string value;
            BoxedString(std::string v = "") : value(v) {}
            std::string __repr__() const { return std::string("BoxedString(") + value + ")"; }
        };
    """,
    )


def test_const_vs_non_const():
    options = litgen.LitgenOptions()
    options.fn_params_replace_modifiable_immutable_by_boxed__regex = ".*"
    cpp_code = """
    void foo_const(const std::string& s);
    void foo_non_const(std::string& s);
    """

    generator = LitgenGenerator(options)
    generator.process_cpp_code(cpp_code, "file.h")

    # logging.warning(f"\nglue_code=\n{generator.glue_code()}")
    code_utils.assert_are_codes_equal(
        generator._boxed_types_cpp_code(),
        """
        struct BoxedString
        {
            std::string value;
            BoxedString(std::string v = "") : value(v) {}
            std::string __repr__() const { return std::string("BoxedString(") + value + ")"; }
        };
    """,
    )

    # logging.warning(f"\nstub_code = \n{generator.stub_code()}")
    code_utils.assert_are_codes_equal(
        generator.stub_code(),
        """
        ####################    <generated_from:BoxedTypes>    ####################
        class BoxedString:
            value: str
            def __init__(self, v: str = "") -> None:
                pass
            def __repr__(self) -> str:
                pass
        ####################    </generated_from:BoxedTypes>    ####################


        ####################    <generated_from:file.h>    ####################

        def foo_const(s: str) -> None:
            pass
        def foo_non_const(s: BoxedString) -> None:
            pass
        ####################    </generated_from:file.h>    ####################
    """,
    )

    code_utils.assert_are_codes_equal(
        generator.pydef_code(),
        """
        ////////////////////    <generated_from:BoxedTypes>    ////////////////////
        auto pyClassBoxedString =
            py::class_<BoxedString>
                (m, "BoxedString", "")
            .def_readwrite("value", &BoxedString::value, "")
            .def(py::init<std::string>(),
                py::arg("v") = "")
            .def("__repr__",
                &BoxedString::__repr__)
            ;
        ////////////////////    </generated_from:BoxedTypes>    ////////////////////


        ////////////////////    <generated_from:file.h>    ////////////////////
        m.def("foo_const",
            foo_const, py::arg("s"));

        m.def("foo_non_const",
            [](BoxedString & s)
            {
                auto foo_non_const_adapt_modifiable_immutable = [](BoxedString & s)
                {
                    std::string & s_boxed_value = s.value;

                    foo_non_const(s_boxed_value);
                };

                foo_non_const_adapt_modifiable_immutable(s);
            },     py::arg("s"));
        ////////////////////    </generated_from:file.h>    ////////////////////
    """,
    )
