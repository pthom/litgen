#include "mylib/api_marker.h"

//
// Modifiable immutable python types test
//

/////////////////////////////////////////////////////////////////////////////////////////////
// Test Part 1: in the functions below, the value parameters will be "Boxed"
//
// This is caused by the following options during generation:
//     options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
//         r"^Toggle",
//         r"^Modify",
//      ]
/////////////////////////////////////////////////////////////////////////////////////////////


// Test with pointer
// -->    def toggle_bool_pointer(v: BoxedBool) -> None:
MY_API void ToggleBoolPointer(bool *v)
{
    *v = !(*v);
}

// Test with nullable pointer
// -->    def toggle_bool_nullable(v: BoxedBool = None) -> None:
MY_API void ToggleBoolNullable(bool *v = NULL)
{
    if (v != NULL)
        *v = !(*v);
}

// Test with reference
// -->    def toggle_bool_reference(v: BoxedBool) -> None:
MY_API void ToggleBoolReference(bool &v)
{
    v = !(v);
}

// Test modifiable String
// -->    def modify_string(s: BoxedString) -> None:
MY_API void ModifyString(std::string* s) { (*s) += "hello"; }


/////////////////////////////////////////////////////////////////////////////////////////////
//
// Test Part 2: in the functions below, the python return type is modified:
// the python functions will return a tuple:
//     (original_return_value, modified_parameter)
//
// This is caused by the following options during generation:
//
//     options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Slider"]
/////////////////////////////////////////////////////////////////////////////////////////////


// Test with int param + int return type
// --> def slider_bool_int(label: str, value: int) -> Tuple[bool, int]:
MY_API bool SliderBoolInt(const char* label, int * value)
{
    *value += 1;
    return true;
}

// -->    def slider_void_int(label: str, value: int) -> int:
MY_API void SliderVoidInt(const char* label, int * value)
{
    *value += 1;
}

// -->    def slider_bool_int2(label: str, value1: int, value2: int) -> Tuple[bool, int, int]:
MY_API bool SliderBoolInt2(const char* label, int * value1, int * value2)
{
    *value1 += 1;
    *value2 += 2;
    return false;
}

// -->    def slider_void_int_default_null(label: str, value: Optional[int] = None) -> Tuple[bool, Optional[int]]:
MY_API bool SliderVoidIntDefaultNull(const char* label, int * value = nullptr)
{
    if (value != nullptr)
        *value += 1;
    return true;
}

// -->    def slider_void_int_array(label: str, value: List[int]) -> Tuple[bool, List[int]]:
MY_API bool SliderVoidIntArray(const char* label, int value[3])
{
    value[0] += 1;
    value[1] += 2;
    value[2] += 3;
    return true;
}
