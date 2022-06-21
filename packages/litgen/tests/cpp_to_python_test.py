import pytest

import litgen
from codemanip import code_utils
from litgen.internal import cpp_to_python


def test_make_boxed_type():
    cpp_numeric_type = "unsigned long long"
    boxed_type = cpp_to_python.BoxedImmutablePythonType(cpp_numeric_type)

    struct_code = boxed_type._struct_code()
    # logging.warning("\n" + struct_code)
    code_utils.assert_are_codes_equal(
        struct_code,
        """
        struct BoxedUnsignedLongLong
        {
            unsigned long long value;
            BoxedUnsignedLongLong() : value{} {}
            BoxedUnsignedLongLong(unsigned long long v) : value(v) {}
            std::string __repr__() const { return std::string("BoxedUnsignedLongLong(") + std::to_string(value) + ")"; }
        };
    """,
    )

    options = litgen.LitgenOptions()
    pydef_code = boxed_type._binding_code(options)
    # logging.warning("\n" + pydef_code)
    expected_code = """
        auto pyClassBoxedUnsignedLongLong = py::class_<BoxedUnsignedLongLong>
            (m, "BoxedUnsignedLongLong", "")
            .def_readwrite("value", &BoxedUnsignedLongLong::value, "")
            .def(py::init<>())
            .def(py::init<unsigned long long>(),
                py::arg("v"))
            .def("__repr__",
                [](const BoxedUnsignedLongLong & self)
                {
                    return self.__repr__();
                }
            )
            ;
    """
    code_utils.assert_are_codes_equal(pydef_code, expected_code)

    with pytest.raises(TypeError):
        a = cpp_to_python.BoxedImmutablePythonType("SomeClass")

    # Test generation of boxed structs code and bindings
    # (We instantiated boxing for "unsigned long long" and "int")
    _ = cpp_to_python.BoxedImmutablePythonType("int")
    boxed_structs_code = cpp_to_python.BoxedImmutablePythonType.struct_codes()
    # logging.warning("\n" + boxed_structs_code)
    code_utils.assert_are_codes_equal(
        boxed_structs_code,
        """
        struct BoxedUnsignedLongLong
        {
            unsigned long long value;
            BoxedUnsignedLongLong() : value{} {}
            BoxedUnsignedLongLong(unsigned long long v) : value(v) {}
            std::string __repr__() const { return std::string("BoxedUnsignedLongLong(") + std::to_string(value) + ")"; }
        };
        struct BoxedInt
        {
            int value;
            BoxedInt() : value{} {}
            BoxedInt(int v) : value(v) {}
            std::string __repr__() const { return std::string("BoxedInt(") + std::to_string(value) + ")"; }
        };
    """,
    )

    binding_codes = cpp_to_python.BoxedImmutablePythonType.binding_codes(options)
    code_utils.assert_are_codes_equal(
        binding_codes,
        """
        auto pyClassBoxedUnsignedLongLong = py::class_<BoxedUnsignedLongLong>
            (m, "BoxedUnsignedLongLong", "")
            .def_readwrite("value", &BoxedUnsignedLongLong::value, "")
            .def(py::init<>())
            .def(py::init<unsigned long long>(),
                py::arg("v"))
            .def("__repr__",
                [](const BoxedUnsignedLongLong & self)
                {
                    return self.__repr__();
                }
            )
            ;
        auto pyClassBoxedInt = py::class_<BoxedInt>
            (m, "BoxedInt", "")
            .def_readwrite("value", &BoxedInt::value, "")
            .def(py::init<>())
            .def(py::init<int>(),
                py::arg("v"))
            .def("__repr__",
                [](const BoxedInt & self)
                {
                    return self.__repr__();
                }
            )
            ;
    """,
    )
