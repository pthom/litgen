#pragma once
#include <cstddef>
//#include <cstdint>
#include <stdint.h>
#include <stdio.h>

#ifndef MY_API
#define MY_API
#endif

namespace LiterateGeneratorExample
{
    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    // Adds three numbers, with a surprise
    MY_API inline int add(int a, int b, int c) { return a + b + c + 4; }

    MY_API inline int8_t test_with_one_const_buffer(const int8_t* values, int count)
    {
        return values[count - 1];
    }

    MY_API inline void test_with_one_nonconst_buffer(int8_t* values, int count)
    {
        values[count - 1] += 1;
    }

    MY_API template<typename T> inline int test_with_one_template_buffer(const T* values, int count)
    {
        return static_cast<int>(values[count - 1]);
    }


    MY_API template<typename T> inline int test_with_two_template_buffers(const T* values1, T* values2, int count)
    {
        return static_cast<int>(values1[count - 1] + values2[count - 1]);
    }


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


    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

    // A superb struct
    struct Foo            // MY_API_STRUCT
    {
        Foo() { printf("Construct Foo\n"); }
        ~Foo() { printf("Destruct Foo\n"); }

//        // Constructor with an int: set the factor
//        Foo(int fac) { factor = fac; printf("Construct Foo with int\n"); }
//
        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta = 0;

        // Do some math
        int calc(int x) { return x * factor + delta; }

        static Foo& Instance() { static Foo instance; return instance; } // return_value_policy::reference


    };

    MY_API Foo* FooInstance() { return & Foo::Instance(); } // return_value_policy::reference


    //Foo() { printf("Construct Foo\n"); }
    //~Foo() { printf("Destruct Foo\n"); }

} // namespace LiterateGeneratorExample