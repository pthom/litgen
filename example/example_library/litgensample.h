#pragma once
#include <cstddef>
//#include <cstdint>
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

namespace LiterateGeneratorExample
{
    // Add
    MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}

    MY_API inline void change_c_array(unsigned long values[2])
    {
        values[0] = values[1] + values[0];
        values[1] = values[0] * values[1];
    }

    //    // Add vector
//    MY_API inline int change_vector(std::vector<int>& values)
//    {
//        int sum = 0;
//        for (auto& v : values)
//            v += 1;
//        return sum;
//    }

    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    // Adds three numbers, with a surprise
    MY_API inline int add(int a, int b, int c) { return a + b + c + 4; }

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
        int calc(int x) { return x * factor + delta; }

        static Foo& Instance() { static Foo instance; return instance; }       // return_value_policy::reference
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