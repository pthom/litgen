#pragma once
#include <cstddef>
#include <cstring>
#include <stdint.h>
#include <stdio.h>
#include <string>
#include <memory>
#include <vector>
#include <array>

#ifndef MY_API
#define MY_API
#endif

#ifdef OBSCURE_OPTION
void SomeFunctionThatShouldNotBeIncluded();
#endif // #ifdef OBSCURE_OPTION


namespace LiterateGeneratorExample // MY_API
{
    // A super nice enum
    // for demo purposes ( bool val = false )
    enum MyEnum     // MY_API
    {
        MyEnum_a = 1, // This is value a
        MyEnum_aa,    // this is value aa
        MyEnum_aaa,   // this is value aaa

        // Lonely comment

        // This is value b
        MyEnum_b,

        // This is c
        // with doc on several lines
        MyEnum_c = MyEnum_a | MyEnum_b,

        MyEnum_count
    };

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

    //
    // C Style buffer to py::array tests
    //

    // Modifies a buffer by adding a value to its elements
    MY_API inline void add_inside_buffer(uint8_t* buffer, size_t buffer_size, uint8_t number_to_add)
    {
        for (size_t i  = 0; i < buffer_size; ++i)
            buffer[i] += number_to_add;
    }
    // Returns the sum of a const buffer
    MY_API inline int buffer_sum(const uint8_t* buffer, size_t buffer_size, size_t stride= sizeof(uint8_t))
    {
        int sum = 0;
        for (size_t i  = 0; i < buffer_size; ++i)
            sum += (int)buffer[i];
        return sum;
    }
    // Modifies two buffers
    MY_API inline void add_inside_two_buffers(uint8_t* buffer_1, uint8_t* buffer_2, size_t buffer_size, uint8_t number_to_add)
    {
        for (size_t i  = 0; i < buffer_size; ++i)
        {
            buffer_1[i] += number_to_add;
            buffer_2[i] += number_to_add;
        }
    }


    // Modify an array by multiplying its elements (template function!)
    template<typename T> MY_API void mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
    {
        for (size_t i  = 0; i < buffer_size; ++i)
            buffer[i] *= (T)factor;
    }

    //
    // C String lists tests
    //

    MY_API inline size_t c_string_list_total_size(const char * const items[], int items_count, int output[2])
    {
        size_t total = 0;
        for (size_t i = 0; i < items_count; ++i)
            total += strlen(items[i]);
        output[0] = total;
        output[1] = total + 1;
        return total;
    }


    //
    // Modifiable immutable python types test
    //
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



    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    // Adds three numbers, with a surprise
    // MY_API inline int add(int a, int b, int c) { return a + b + c + 4; }


    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

    // A superb struct
    struct Foo            // MY_API
    {
        Foo() { printf("Construct Foo\n");}
        ~Foo() { printf("Destruct Foo\n"); }

        //
        // These are our parameters
        //

        //
        // Test with numeric arrays which should be converted to py::array
        //
        int values[2] = {0, 1};
        bool flags[3] = {false, true, false};

        // These should not be exported (cannot fit in a py::array)
        Point2 points[2];

        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta;

        //
        // And these are our calculations
        //

        // Do some math
        MY_API int calc(int x) { return x * factor + delta; }

        static Foo& Instance() { static Foo instance; return instance; }       // return_value_policy::reference
    };

    MY_API Foo* FooInstance() { return & Foo::Instance(); } // return_value_policy::reference



    //
    // Test overload
    //
    MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
    MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore

    struct FooOverload // MY_API
    {
        MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
        MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore
    };

    //
    // Test Boxed String
    //
    MY_API void ModifyString(std::string* s) { (*s) += "hello"; }

//
} // namespace LiterateGeneratorExample
