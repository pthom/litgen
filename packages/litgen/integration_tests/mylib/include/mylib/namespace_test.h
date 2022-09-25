#include "mylib/api_marker.h"

// This is the root namespace
namespace Root // MY_API
{

    // This is the main namespace
    namespace Main      // MY_API
    {
        MY_API void foo();

        enum Bidule // MY_API
        {
            a, b, c
        };
    }
}
