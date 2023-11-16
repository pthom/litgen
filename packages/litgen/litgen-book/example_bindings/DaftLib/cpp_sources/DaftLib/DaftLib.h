#include "DaftLib/DaftLib2.h"

namespace DaftLib
{
    int Add(int a, int b);

    // In this example, the parameter v will be "Boxed" into a "BoxedBool"
    inline void SwitchBool(bool& v)
    {
        v = !v;
    }
}
