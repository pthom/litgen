// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: c_extern_c.h
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
    ////////////////////    <generated_from:c_extern_c.h>    ////////////////////
    // #ifdef __cplusplus
    //
    // #endif
    //

    m.def("extern_c_add",
        extern_c_add, py::arg("a"), py::arg("b"));

    m.def("foo_void_param",
        foo_void_param);

    m.def("foo_unnamed_param",
        foo_unnamed_param, py::arg("param_0"), py::arg("param_1"), py::arg("param_2"));
    m.attr("ANSWER_ZERO_COMMENTED") = 0;
    m.attr("ANSWER_ONE_COMMENTED") = 1;
    m.attr("HEXVALUE") = 0x43242;
    m.attr("OCTALVALUE") = 043242;
    m.attr("STRING") = "Hello";
    m.attr("FLOAT") = 3.14;
    // #ifdef __cplusplus
    //
    // #endif
    //
    ////////////////////    </generated_from:c_extern_c.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}
