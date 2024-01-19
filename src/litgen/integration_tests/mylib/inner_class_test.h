#include "api_marker.h"


namespace SomeNamespace
{
    struct ParentStruct
    {
        struct InnerStruct
        {
            int value;

            InnerStruct(int value = 10) : value(value) {}
            MY_API int add(int a, int b) { return a + b; }
        };

        enum class InnerEnum
        {
            Zero = 0,
            One,
            Two,
            Three
        };

        InnerStruct inner_struct = InnerStruct();
        InnerEnum inner_enum = InnerEnum::Three;
    };
} // namespace SomeNamespace
