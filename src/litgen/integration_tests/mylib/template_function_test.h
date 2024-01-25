#include "api_marker.h"

#include <string>

// AddTemplated is a template function that will be implemented for the types ["int", "double", "std::string"]
//
// See inside autogenerate_mylib.py:
//     options.fn_template_options.add_specialization(r"^AddTemplated$", ["int", "double", "std::string"])

template<typename T>
MY_API T AddTemplated(T a, T b)
{
    return  a + b;
}


// SumVectorAndCArray is a template function that will be implemented for the types ["int", "std::string"]
//
// Here, we test two additional thing:
//  - nesting of the T template parameter into a vector
//  - mixing template and function parameter adaptations (here other_values[2] will be transformed into a List[T]
//
// See inside autogenerate_mylib.py:
//     options.fn_template_options.SumVectorAndCArray(r"^SumVector", ["int", "std::string"])

template<typename T>
MY_API T SumVectorAndCArray(std::vector<T> xs, const T other_values[2])
{
    T sum = T{};
    for (const T & v: xs )
        sum += v;
    sum += other_values[0];
    sum += other_values[1];
    return sum;
}


// Same test, as a method

struct FooTemplateFunctionTest
{
    template<typename T>
    MY_API T SumVectorAndCArray(std::vector<T> xs, const T other_values[2])
    {
        T sum = T{};
        for (const T & v: xs )
            sum += v;
        sum += other_values[0];
        sum += other_values[1];
        return sum;
    }
};
