#include "api_marker.h"
#include <string>


namespace A
{
    enum class Foo
    {
        Foo1 = 0,
        Foo2 = 1,
        Foo3 = 2
    };

    // This struct has no default constructor, so a default named constructor
    // will be provided for python
    struct ClassNoDefaultCtor
    {
        bool b = true;
        int a;
        int c = 3;
        Foo foo = Foo::Foo1;
        const std::string s = "Allo";
    };

    namespace N
    {
        struct S {};
        enum class EC { a = 0 };
        enum E { E_a = 0 };

        MY_API void Foo(EC e = EC::a) {}
        MY_API void Foo(E e = E_a) {}
        MY_API void Foo(S s = S(), E e = E_a) {}
    }

}
