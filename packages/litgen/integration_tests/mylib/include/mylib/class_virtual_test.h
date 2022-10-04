#include "mylib/api_marker.h"

namespace Root  // MY_API
{
    namespace Inner // MY_API
    {
        class MyVirtualClass // MY_API
        {
        protected:
            MY_API int foo() const { return 42; }
            MY_API int foo2() const { return 44; }
            MY_API int foo3() const { return 46; }
        };
    }
}
