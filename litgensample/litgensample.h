#pragma once
#include <cstddef>
//#include <cstdint>
#include <stdint.h>

#ifndef MY_API
#define MY_API
#endif

namespace LiterateGeneratorExample
{
    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    // Adds three numbers, with a surprise
    MY_API inline int add(int a, int b, int c) { return a + b + c + 4; }

    // Modify an array by adding a value to its elements
    MY_API inline void add_inside_array(uint8_t* array, size_t array_size, uint8_t number_to_add)
    {
        for (size_t i  = 0; i < array_size; ++i)
            array[i] += number_to_add;
    }

    // Modify an array by adding a value to its elements
    MY_API template<typename T> void mul_inside_array(T* array, size_t array_size, double factor)
    {
        for (size_t i  = 0; i < array_size; ++i)
            array[i] *= (T)factor;
    }


    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

    // A superb struct
    struct Foo
    {
        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta = 0;

        // Do some math
        int calc(int x) { return x * factor + delta; }
    };

} // namespace LiterateGeneratorExample