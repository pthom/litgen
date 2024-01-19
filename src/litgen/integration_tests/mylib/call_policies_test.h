#include "api_marker.h"

#include <iostream>

struct CallGuardLogger;


// ============================================================================
// call_guard
// ============================================================================
// If you add a comment to the function with reads:
//     py::call_guard<YourCallGuard>()
// Then, it will be taken into account
// See https://pybind11.readthedocs.io/en/stable/advanced/functions.html#call-guard
// The comment may be a comment on previous line or an end-of-line comment

MY_API void call_guard_tester() // py::call_guard<CallGuardLogger>()
{
    std::cout << "call_guard_tester\n";
}


// ============================================================================
// keep-alive
// ============================================================================
// If you add a comment to the function with reads:
//     py::keep-alive<1, 2>()
// Then, it will be taken into account
// See https://pybind11.readthedocs.io/en/stable/advanced/functions.html#keep-alive
// The comment may be a comment on previous line or an end-of-line comment
//
// (No integration test implemented for this)


// ============================================================================
// return value policy
// => see doc inside return_value_policy_test.h
// ============================================================================


// ============================================================================
// CallGuardLogger: dummy call guard for the tests
// ============================================================================
struct CallGuardLogger
{
    CallGuardLogger() {
        ++nb_construct;
    }
    ~CallGuardLogger() {
        ++nb_destroy;
    }

    static int nb_construct;
    static int nb_destroy;
};

int CallGuardLogger::nb_construct = 0;
int CallGuardLogger::nb_destroy = 0;
