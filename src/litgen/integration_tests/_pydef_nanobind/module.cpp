#include <nanobind/nanobind.h>


namespace py = nanobind;


void py_init_module_lg_mylib(py::module_& m);


// This builds the native python module `_testrunner`
// it will be wrapped in a standard python module `testrunner`
NB_MODULE(_lg_mylib_nanobind, m)
{
    py_init_module_lg_mylib(m);
}
