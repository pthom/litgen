#include "mylib/api_marker.h"

//
// C Style array tests
//

// Tests with Boxed Numbers
MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}
MY_API inline void log_c_array2(const int values[2]) { printf("%i, %i\n", values[0], values[1]); }
MY_API inline void change_c_array2(unsigned long values[2])
{
    values[0] = values[1] + values[0];
    values[1] = values[0] * values[1];
}
// Test with C array containing user defined struct (which will not be boxed)
struct Point2 // MY_API
{
    int x, y;
};
MY_API inline void GetPoints(Point2 out[2]) { out[0] = {0, 1}; out[1] = {2, 3}; }
