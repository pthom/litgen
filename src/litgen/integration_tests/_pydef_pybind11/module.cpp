#include <pybind11/pybind11.h>


namespace py = pybind11;


void py_init_module_lg_mylib(py::module& m);


// This builds the native python module `_testrunner`
// it will be wrapped in a standard python module `testrunner`
PYBIND11_MODULE(_lg_mylib_pybind, m)
{
    py_init_module_lg_mylib(m);
}
