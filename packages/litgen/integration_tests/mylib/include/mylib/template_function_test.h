#include "mylib/mylib.h"

#include <string>

// AddTemplated is a template function that will be implemented for the types ["int", "double", "std::string"]
//
// See autogenerate_mylib.py:
//     options.fn_template_functions_options[r"^AddTemplated$"] = ["int", "double", "std::string"]

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
// See autogenerate_mylib.py:
//     options.fn_template_functions_options[r"^SumVector"] = ["int", "std::string"]

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


/*
For info, here are the generated python stub signatures:

def add_templated(a: int, b: int) -> int:
    pass
def add_templated(a: float, b: float) -> float:
    pass
def add_templated(a: str, b: str) -> str:
    pass

def sum_vector_and_c_array(xs: List[int], other_values: List[int]) -> int:
    pass
def sum_vector_and_c_array(xs: List[str], other_values: List[str]) -> str:
    pass

 */
