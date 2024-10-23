// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: _bind_type.h
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
    ////////////////////    <generated_from:_bind_type.h>    ////////////////////
    m.def("bindings_with_nanobind",
        bindings_with_nanobind);

    m.def("bindings_with_pybind",
        bindings_with_pybind);
    ////////////////////    </generated_from:_bind_type.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}