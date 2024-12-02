from __future__ import annotations
from codemanip import code_utils
import litgen
from litgen.internal.adapted_types import AdaptedFunction

from srcmlcpp.cpp_types import CppPublicProtectedPrivate


def test_reference_marking():
    """
    Example of how the callback mechanism could be used in practice to handle reference return policies
    """

    def test_custom_reference_detection(func: AdaptedFunction) -> None:
        if not func.return_value_policy:
            # In this example, all methods which return a reference or pointer
            # will be marked with a custom return_value_policy attribute: "reference_internal"
            # func.return_value_policy attribute, will be applied in pybind11 / nanobind code
            if isinstance(func.cpp_element().parent, CppPublicProtectedPrivate):  # if it is a member function
                if hasattr(func.cpp_element(), "return_type") and (
                    "&" in func.cpp_element().return_type.modifiers or "*" in func.cpp_element().return_type.modifiers
                ):
                    func.return_value_policy = "reference_internal"

            # Another custom policy could be applied based on the filename (not relevant for this test)
            elif func.cpp_adapted_function.filename and "ref_stuf" in func.cpp_adapted_function.filename:
                func.return_value_policy = "reference"
            # or based on the function name
            elif "ByRef" in func.cpp_adapted_function.function_name:
                func.return_value_policy = "reference"

    code = """
        class MyClass {
        public:
            MyClass& setValue(int value) { _value = value; return *this; }
            int getValue() const { return _value; }
            AnotherClass& getReferenceObject() { return _referenceObject; }

        private:
            int _value;
            AnotherClass _referenceObject;
        };
        MyClass& testFunction();
        MyClass& testFunctionByRef();
    """

    options = litgen.LitgenOptions()
    options.fn_return_force_policy_reference__callback = test_custom_reference_detection
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassMyClass =
            py::class_<MyClass>
                (m, "MyClass", "")
            .def(py::init<>()) // implicit default constructor
            .def("set_value",
                &MyClass::setValue,
                py::arg("value"),
                py::return_value_policy::reference_internal)
            .def("get_value",
                &MyClass::getValue)
            .def("get_reference_object",
                &MyClass::getReferenceObject, py::return_value_policy::reference_internal)
            ;


        m.def("test_function",
            testFunction);

        m.def("test_function_by_ref",
            testFunctionByRef, py::return_value_policy::reference);
      """,
    )
