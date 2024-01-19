#include "api_marker.h"

#include "string.h"

//
// C String lists tests:
//   Two consecutive params (const char *, int | size_t) are exported as List[str]
//
// The following function will be exported with the following python signature:
// -->    def c_string_list_total_size(items: List[str], output_0: BoxedInt, output_1: BoxedInt) -> int:
//
MY_API inline size_t c_string_list_total_size(const char * const items[], int items_count, int output[2])
{
    size_t total = 0;
    for (size_t i = 0; i < items_count; ++i)
        total += strlen(items[i]);
    output[0] = (int)total;
    output[1] = (int)(total + 1);
    return total;
}
