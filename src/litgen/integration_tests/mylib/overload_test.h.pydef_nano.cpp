// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: overload_test.h
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
    ////////////////////    <generated_from:overload_test.h>    ////////////////////
    m.def("add_overload",
        py::overload_cast<int, int>(add_overload), py::arg("a"), py::arg("b"));

    m.def("add_overload",
        py::overload_cast<int, int, int>(add_overload), py::arg("a"), py::arg("b"), py::arg("c"));


    auto pyClassFooOverload =
        py::class_<FooOverload>
            (m, "FooOverload", "")
        .def(py::init<>()) // implicit default constructor
        .def("add_overload",
            py::overload_cast<int, int>(&FooOverload::add_overload), py::arg("a"), py::arg("b"))
        .def("add_overload",
            py::overload_cast<int, int, int>(&FooOverload::add_overload), py::arg("a"), py::arg("b"), py::arg("c"))
        ;
    ////////////////////    </generated_from:overload_test.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}