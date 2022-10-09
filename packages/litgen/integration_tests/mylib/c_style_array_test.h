#include "api_marker.h"

//
// C Style array tests
//


// Tests with const array: since the input numbers are const, their params are published as List[int],
// and the python signature will be:
// -->    def add_c_array2(values: List[int]) -> int:
// (and the runtime will check that the list size is exactly 2)
MY_API inline int const_array2_add(const int values[2]) { return values[0] + values[1];}


// Test with a modifiable array: since the input array is not const, it could be modified.
// Thus, it will be published as a function accepting Boxed values:
// -->    def array2_modify(values_0: BoxedUnsignedLong, values_1: BoxedUnsignedLong) -> None:
MY_API inline void array2_modify(unsigned long values[2])
{
    values[0] = values[1] + values[0];
    values[1] = values[0] * values[1];
}

struct Point2
{
    int x, y;
};

// Test with a modifiable array that uses a user defined struct.
// Since the user defined struct is mutable in python, it will not be Boxed,
// and the python signature will be:
//-->    def get_points(out_0: Point2, out_1: Point2) -> None:
MY_API inline void array2_modify_mutable(Point2 out[2]) { out[0] = {0, 1}; out[1] = {2, 3}; }
