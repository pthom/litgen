#include <pybind11/pybind11.h>


namespace py = pybind11;


void py_init_module_testrunner(py::module& m);


// This builds the native python module `_testrunner`
// it will be wrapped in a standard python module `testrunner`
PYBIND11_MODULE(_testrunner, m)
{
    #ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
    #else
    m.attr("__version__") = "dev";
    #endif

    py_init_module_testrunner(m);
}
