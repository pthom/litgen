#pragma once
#include <cstddef>
#include <cstring>
#include <stdint.h>
#include <stdio.h>
#include <string>
#include <memory>
#include <vector>
#include <array>

#include "mylib/api_marker.h"
#include "mylib/basic_test.h"
#include "mylib/header_filter_test.h"
#include "mylib/c_style_array_test.h"
#include "mylib/c_style_buffer_to_pyarray_test.h"
#include "mylib/c_string_list_test.h"
#include "mylib/modifiable_immutable_test.h"
#include "mylib/overload_test.h"
#include "mylib/enum_test.h"


namespace LiterateGeneratorExample // MY_API
{


    // A superb struct
    struct Foo            // MY_API
    {
        Foo() { printf("Construct Foo\n");}
        ~Foo() { printf("Destruct Foo\n"); }

        //
        // These are our parameters
        //

        //
        // Test with numeric arrays which should be converted to py::array
        //
        int values[2] = {0, 1};
        bool flags[3] = {false, true, false};

        // These should not be exported (cannot fit in a py::array)
        Point2 points[2];

        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta;

        //
        // And these are our calculations
        //

        // Do some math
        MY_API int calc(int x) { return x * factor + delta; }

        static Foo& Instance() { static Foo instance; return instance; }  // return_value_policy::reference
    };

    MY_API Foo* FooInstance() { return & Foo::Instance(); } // return_value_policy::reference





} // namespace LiterateGeneratorExample
