// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: namespace_test.h
// It is not used in the compilation
//    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
//     code, including this code)
// ============================================================================

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include "mylib/mylib_main/mylib.h"

namespace py = pybind11;

// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end


void py_init_module_mylib(py::module& m)
{
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:namespace_test.h>    ////////////////////
    m.def("foo_root",
        FooRoot);

    { // <namespace Inner>
        py::module_ pyNsInner = m.def_submodule("inner", "this is an inner namespace (this comment should become the namespace doc)");
        pyNsInner.def("foo_inner",
            Mylib::Inner::FooInner);
        pyNsInner.def("foo_inner2",
            Mylib::Inner::FooInner2);
    } // </namespace Inner>
    ////////////////////    </generated_from:namespace_test.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}
