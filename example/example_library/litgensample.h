#pragma once
#include <cstddef>
#include <cstring>
#include <stdint.h>
#include <stdio.h>
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
    //
    // C Style array tests
    //

    MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}
    MY_API inline void log_c_array2(const int values[2]) { printf("%i, %i\n", values[0], values[1]); }
    MY_API inline void change_c_array2(unsigned long values[2])
    {
        values[0] = values[1] + values[0];
        values[1] = values[0] * values[1];
    }


    //
    // C Style buffer to py::array tests
    //

    // Modify an array by adding a value to its elements (*non* template function)
    MY_API inline void add_inside_array(uint8_t* array, size_t array_size, uint8_t number_to_add)
    {
        for (size_t i  = 0; i < array_size; ++i)
            array[i] += number_to_add;
    }
    // Modify an array by multiplying its elements (template function!)
    MY_API template<typename T> void mul_inside_array(T* array, size_t array_size, double factor)
    {
        for (size_t i  = 0; i < array_size; ++i)
            array[i] *= (T)factor;
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


    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    // Adds three numbers, with a surprise
    MY_API inline int add(int a, int b, int c) { return a + b + c + 4; }


    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

    // A superb struct
    struct Foo            // MY_API
    {
        Foo() { printf("Construct Foo\n"); }
        ~Foo() { printf("Destruct Foo\n"); }

        //
        // These are our parameters
        //

        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta;

        //
        // And these are our calculations
        //

        // Do some math
        MY_API int calc(int x) { return x * factor + delta; }

        MY_API static Foo& Instance() { static Foo instance; return instance; }       // return_value_policy::reference
    };

    MY_API Foo* FooInstance() { return & Foo::Instance(); } // return_value_policy::reference

//    MY_API void ToggleBool(bool *v) {
//        printf("ToggleBool ptr=%p value=%s\n", v, (*v) ? "True" : "False");
//        *v = !(*v);
//    }
//
//    MY_API void ToggleBool2(std::shared_ptr<bool> v) {
//        bool *b = v.get();
//        printf("ToggleBool2 ptr=%p value=%s\n", b, (*b) ? "True" : "False");
//        *b = !(*b);
//    }
//
} // namespace LiterateGeneratorExample