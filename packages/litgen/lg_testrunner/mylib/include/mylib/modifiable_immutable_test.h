#include "mylib/api_marker.h"

//
// Modifiable immutable python types test
//


//
// Test Part 1: in those functions the value parameters will be "Boxed"
//
// This is caused by the following options during generation:
//     options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
//         r"^Toggle",
//         r"^Modify",
//      ]

// Test with pointer
MY_API void ToggleBoolPointer(bool *v)
{
    *v = !(*v);
}

// Test with nullable pointer
MY_API void ToggleBoolNullable(bool *v = NULL)
{
    if (v != NULL)
        *v = !(*v);
}

// Test with reference
MY_API void ToggleBoolReference(bool &v)
{
    v = !(v);
}

MY_API bool SliderBoolInt(const char* label, int * value)
{
    *value += 1;
    return true;
}

// Test modifiable String
MY_API void ModifyString(std::string* s) { (*s) += "hello"; }


//
// Test Part 2: in the functions below return type is modified:
// the following functions will return a tuple inside python :
//     (original_return_value, modified_paramer)
//
// This is caused by the following options during generation:
//
//     options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Slider"]


MY_API void SliderVoidInt(const char* label, int * value)
{
    *value += 1;
}

MY_API bool SliderBoolInt2(const char* label, int * value1, int * value2)
{
    *value1 += 1;
    *value2 += 2;
    return false;
}

MY_API bool SliderVoidIntDefaultNull(const char* label, int * value = nullptr)
{
    if (value != nullptr)
        *value += 1;
    return true;
}

MY_API bool SliderVoidIntArray(const char* label, int value[3])
{
    value[0] += 1;
    value[1] += 2;
    value[2] += 3;
    return true;
}
