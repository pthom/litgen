#include "mylib/api_marker.h"

//
// C String lists tests
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
