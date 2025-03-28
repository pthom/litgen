// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: qualified_scoping_test.h
// It is not used in the compilation
//    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
//     code, including this code)
// ============================================================================

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/function.h>
#include "mylib_main/mylib.h"

namespace py = nanobind;

// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end


void py_init_module_mylib(py::module_& m)
{
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:qualified_scoping_test.h>    ////////////////////

    { // <namespace N>
        py::module_ pyNsN = m.def_submodule("n", "");
        auto pyNsN_ClassS =
            py::class_<N::S>
                (pyNsN, "S", "")
            .def(py::init<>()) // implicit default constructor
            ;


        auto pyEnumEC =
            py::enum_<N::EC>(pyNsN, "EC", py::is_arithmetic(), "")
                .value("a", N::EC::a, "");


        auto pyEnumE =
            py::enum_<N::E>(pyNsN, "E", py::is_arithmetic(), "")
                .value("a", N::E_a, "");


        pyNsN.def("foo",
            py::overload_cast<N::EC>(N::Foo), py::arg("e") = N::EC::a);

        pyNsN.def("foo",
            py::overload_cast<N::E>(N::Foo), py::arg("e") = N::E_a);

        pyNsN.def("foo",
            py::overload_cast<N::E, N::S>(N::Foo), py::arg("e") = N::E_a, py::arg("s") = N::S());
    } // </namespace N>
    ////////////////////    </generated_from:qualified_scoping_test.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}
