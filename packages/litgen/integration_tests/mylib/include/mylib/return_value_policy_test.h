#include "mylib/api_marker.h"

//
// return_value_policy:
//
// If a function has an end-of-line comment which contains `return_value_policy::reference`,
// and if this function returns a pointer or a reference, litgen will automatically add
// `pybind11::return_value_policy::reference` when publishing it.
//
// Notes: `reference` could be replaced by `take_ownership`, or any other member of `pybind11::return_value_policy`
//
// You can also set a global options for matching functions names that return a reference or a pointer
//     see
//             LitgenOptions.fn_return_force_policy_reference_for_pointers__regex
//     and
//             LitgenOptions.fn_return_force_policy_reference_for_references__regex: str = ""


struct MyConfig
{
    //
    // For example, singletons (such as the method below) should be returned as a reference,
    // otherwise python might destroy the singleton instance as soon as it goes out of scope.
    //

    MY_API static MyConfig& Instance() // py::return_value_policy::reference
    {
        static MyConfig instance;
        return instance;
    }

    int value = 0;
};

MY_API MyConfig* MyConfigInstance() { return & MyConfig::Instance(); } // py::return_value_policy::reference


/*
For info, below is the C++ generated binding code:

     auto pyClassMyConfig = py::class_<MyConfig>
        (m, "MyConfig", "")
        .def(py::init<>()) // implicit default constructor
        .def_readwrite("value", &MyConfig::value, "")
        .def("instance",
            &MyConfig::Instance,
            " Instance() is a method that returns a pointer that should use `return_value_policy::reference`\nreturn_value_policy::reference",
            pybind11::return_value_policy::reference)
        ;


    m.def("my_config_instance",
        MyConfigInstance,
        "return_value_policy::reference",
        pybind11::return_value_policy::reference);


*/
