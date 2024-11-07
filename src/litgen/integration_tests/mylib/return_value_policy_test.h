#include "api_marker.h"

//
// return_value_policy:
//
// If a function has an end-of-line comment which contains
//    `return_value_policy::reference` or `rv_policy::reference` (for nanobind),
// and if this function returns a pointer or a reference, litgen will automatically add
// `pybind11::return_value_policy::reference` when publishing it.
//
// Notes: `reference` could be replaced by `take_ownership`,
//   or any other member of `pybind11::return_value_policy` or `nb::rv_policy` (for nanobind)
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

    MY_API static MyConfig& Instance() // return_value_policy::reference
    {
        static MyConfig instance;
        return instance;
    }

    int value = 0;
};

MY_API MyConfig* MyConfigInstance() { return & MyConfig::Instance(); } // return_value_policy::reference
