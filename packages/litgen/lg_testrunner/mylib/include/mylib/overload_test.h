#include "mylib/mylib.h"

//
// litgen is able to detect automatically the presence of overloads that require
// to use `py::overload_cast<...>` when publishing
//

//
// overload on free functions
//

MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore

//
// overload on methods
//

struct FooOverload // MY_API
{
    MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
    MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore
};


/*
For info, below is the generated C++ code that will publish these functions:

     m.def("add_overload",
        py::overload_cast<int, int>(add_overload), py::arg("a"), py::arg("b"));
    m.def("add_overload",
        py::overload_cast<int, int, int>(add_overload), py::arg("a"), py::arg("b"), py::arg("c"));


    auto pyClassFooOverload = py::class_<FooOverload>
        (m, "FooOverload", "")
        .def(py::init<>()) // implicit default constructor
        .def("add_overload",
            py::overload_cast<int, int>(&FooOverload::add_overload), py::arg("a"), py::arg("b"))
        .def("add_overload",
            py::overload_cast<int, int, int>(&FooOverload::add_overload), py::arg("a"), py::arg("b"), py::arg("c"))
        ;
*/
