#include "mylib/api_marker.h"

struct IntWrapper // MY_API
{
    int value;
    IntWrapper(int v) : value(v) {}

    // arithmetic operators
    MY_API IntWrapper operator+(IntWrapper b) { return IntWrapper{ value + b.value}; }
    MY_API IntWrapper operator-(IntWrapper b) { return IntWrapper{ value - b.value }; }

    // Unary minus operator
    MY_API IntWrapper operator-() { return IntWrapper{ -value }; }

    // Comparison operator
    MY_API bool operator<(IntWrapper b) { return value < b.value; }

    // Two overload of the += operator
    MY_API IntWrapper operator+=(IntWrapper b) { value += b.value; return *this; }
    MY_API IntWrapper operator+=(int b) { value += b; return *this; }

    // Two overload of the call operator, with different results
    MY_API int operator()(IntWrapper b) { return value * b.value + 2; }
    MY_API int operator()(int b) { return value * b + 3; }
};
