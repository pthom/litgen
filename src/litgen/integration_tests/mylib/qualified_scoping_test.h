#pragma once
#include "api_marker.h"


namespace N
{
    struct S {};
    enum class EC { a = 0 };
    enum E { E_a = 0 };

    MY_API void Foo(EC e = EC::a) {}
    MY_API void Foo(E e = E_a) {}
    MY_API void Foo(S s = S(), E e = E_a) {}
}
