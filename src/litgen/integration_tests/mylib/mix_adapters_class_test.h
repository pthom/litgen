// More complex tests, where we combine litgen function adapters with classes and namespace
//
// The main intent of these tests is to verify that the generated code compiles.
// The corresponding python test file will not test all these functions
// (as they are in fact copy/pasted/adapted from other tests)
//

#include "api_marker.h"

#include <cstddef>
#include <string>

namespace SomeNamespace
{
    struct Blah
    {
        MY_API void ToggleBoolPointer(bool *v)//, int vv[2])
        {
            *v = !(*v);
        }

        MY_API void ToggleBoolPointerGetPoints(bool *v, int vv[2])
        {
            *v = !(*v);
        }


        MY_API void ModifyString(std::string* s) { (*s) += "hello"; }



        MY_API bool ChangeBoolInt(const char* label, int * value)
        {
            *value += 1;
            return true;
        }


        MY_API inline void add_inside_buffer(uint8_t* buffer, size_t buffer_size, uint8_t number_to_add)
        {
            for (size_t i  = 0; i < buffer_size; ++i)
                buffer[i] += number_to_add;
        }

        template<typename T> MY_API void templated_mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
        {
            for (size_t i  = 0; i < buffer_size; ++i)
                buffer[i] *= (T)factor;
        }

        MY_API inline int const_array2_add(const int values[2]) { return values[0] + values[1];}

        MY_API inline size_t c_string_list_total_size(const char * const items[], int items_count, int output[2])
        {
            size_t total = 0;
            for (size_t i = 0; i < items_count; ++i)
                total += strlen(items[i]);
            output[0] = (int)total;
            output[1] = (int)(total + 1);
            return total;
        }

    }; // struct Blah


    namespace SomeInnerNamespace
    {
        MY_API void ToggleBoolPointer(bool *v)//, int vv[2])
        {
            *v = !(*v);
        }

        MY_API void ToggleBoolPointerGetPoints(bool *v, int vv[2])
        {
            *v = !(*v);
        }


        MY_API void ModifyString(std::string* s) { (*s) += "hello"; }



        MY_API bool ChangeBoolInt(const char* label, int * value)
        {
            *value += 1;
            return true;
        }


        MY_API inline void add_inside_buffer(uint8_t* buffer, size_t buffer_size, uint8_t number_to_add)
        {
            for (size_t i  = 0; i < buffer_size; ++i)
                buffer[i] += number_to_add;
        }

        template<typename T> MY_API void templated_mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
        {
            for (size_t i  = 0; i < buffer_size; ++i)
                buffer[i] *= (T)factor;
        }

        MY_API inline int const_array2_add(const int values[2]) { return values[0] + values[1];}

        MY_API inline size_t c_string_list_total_size(const char * const items[], int items_count, int output[2])
        {
            size_t total = 0;
            for (size_t i = 0; i < items_count; ++i)
                total += strlen(items[i]);
            output[0] = (int)total;
            output[1] = (int)(total + 1);
            return total;
        }

    } // namespace SomeInnerNamespace

}
