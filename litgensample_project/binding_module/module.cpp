#include <pybind11/pybind11.h>


namespace py = pybind11;


void py_init_module_litgensample(py::module& m);
// void py_init_my_submodule(py::module&);


PYBIND11_MODULE(litgensample, m)
{
    #ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
    #else
    m.attr("__version__") = "dev";
    #endif

    py_init_module_litgensample(m);

    // py::module my_submodule = m.def_submodule("my_submodule");
    // py_init_my_submodule(my_submodule);
}
