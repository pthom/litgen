#include "api_marker.h"


MY_API int FooRoot() { return 42; }

namespace details // MY_API This namespace should be excluded (see options.namespace_exclude__regex)
{
    MY_API int FooDetails() { return 43; }
}

namespace // MY_API This anonymous namespace should be excluded
{
    MY_API int LocalFunction() { return 44; }
}

namespace Mylib  // MY_API This namespace should not be outputted as a submodule (it is considered a root namespace)
{
    // this is an inner namespace (this comment should become the namespace doc)
    namespace Inner
    {
        MY_API int FooInner() { return 45; }
    }

    // This is a second occurrence of the same inner namespace
    // The generated python module will merge these occurrences
    // (and this comment will be ignored, since the Inner namespace already has a doc)
    namespace Inner
    {
        MY_API int FooInner2() { return 46; }
    }
}
