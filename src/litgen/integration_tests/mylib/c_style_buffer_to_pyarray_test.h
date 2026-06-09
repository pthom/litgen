#include "api_marker.h"

#include <stdint.h>
#include <stddef.h>

//
// C Style buffer to py::array tests
//
// litgen is able to recognize and transform pairs of params whose C++ signature resemble
//     (T* data, size_t|int count)
// Where
//   * `T` is a *known* numeric type, or a templated type
//   * `count` name resemble a size
//        (see LitgenOptions.fn_params_buffer_size_names__regex)
//

// add_inside_buffer: modifies a buffer by adding a value to its elements
// Will be published in python as:
// -->    def add_inside_buffer(buffer: np.ndarray, number_to_add: int) -> None:
// Warning, the python function will accept only uint8 numpy arrays, and check it at runtime!
MY_API inline void add_inside_buffer(uint8_t* buffer, size_t buffer_size, uint8_t number_to_add)
{
    for (size_t i  = 0; i < buffer_size; ++i)
        buffer[i] += number_to_add;
}

// buffer_sum: returns the sum of a *const* buffer
// Will be published in python as:
// -->    def buffer_sum(buffer: np.ndarray, stride: int = -1) -> int:
MY_API inline int buffer_sum(const uint8_t* buffer, size_t buffer_size, size_t stride= sizeof(uint8_t))
{
    int sum = 0;
    for (size_t i  = 0; i < buffer_size; ++i)
        sum += (int)buffer[i];
    return sum;
}

// add_inside_two_buffers: modifies two mutable buffers
// litgen will detect that this function uses two buffers of same size.
// Will be published in python as:
// -->    def add_inside_two_buffers(buffer_1: np.ndarray, buffer_2: np.ndarray, number_to_add: int) -> None:
MY_API inline void add_inside_two_buffers(uint8_t* buffer_1, uint8_t* buffer_2, size_t buffer_size, uint8_t number_to_add)
{
    for (size_t i  = 0; i < buffer_size; ++i)
    {
        buffer_1[i] += number_to_add;
        buffer_2[i] += number_to_add;
    }
}

// templated_mul_inside_buffer: template function that modifies an array by multiplying its elements by a given factor
// litgen will detect that this function can be published as using a numpy array.
// It will be published in python as:
// -->    def mul_inside_buffer(buffer: np.ndarray, factor: float) -> None:
//
// The type will be detected at runtime and the correct template version will be called accordingly!
// An error will be thrown if the numpy array numeric type is not supported.
template<typename T> MY_API void templated_mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
{
    for (size_t i  = 0; i < buffer_size; ++i)
        buffer[i] *= (T)factor;
}

// templated_sum_buffers: sums two buffers that must share the same templated type T.
// litgen detects two templated buffers followed by a single size param.
// Will be published in python as:
// -->    def templated_sum_buffers(buffer_1: np.ndarray, buffer_2: np.ndarray) -> float:
//
// Since the function is templated on a single type T, both numpy arrays must share the same dtype:
// the dtype is detected at runtime from the last buffer, and an explicit error is thrown if the other
// buffers have a different dtype (otherwise their bytes would be silently reinterpreted).
template<typename T> MY_API double templated_sum_buffers(const T* buffer_1, const T* buffer_2, size_t buffer_size)
{
    double sum = 0.;
    for (size_t i  = 0; i < buffer_size; ++i)
        sum += (double)(buffer_1[i] + buffer_2[i]);
    return sum;
}
