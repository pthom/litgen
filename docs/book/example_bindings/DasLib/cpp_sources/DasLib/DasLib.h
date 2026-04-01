#include "DasLib/DasLib2.h"

namespace DasLib
{
    int Add(int a, int b);

    // In this example, the parameter v will be "Boxed" into a "BoxedBool"
    inline void SwitchBool(bool& v)
    {
        v = !v;
    }
}
