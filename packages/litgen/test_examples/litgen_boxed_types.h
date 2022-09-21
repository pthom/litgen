#pragma once
#include <string>

//namespace litgen
//{

    using Char = char;
    using UnsignedChar = unsigned char;
    using Short = short;
    using UnsignedShort = unsigned short;
    using Int = int;
    using UnsignedInt = unsigned int;
    using Long = long;
    using UnsignedLong = unsigned long;
    using LongLong = long long;
    using UnsignedLongLong = unsigned long long;
    using Float = float;
    using Double = double;
    using LongDouble = long double;

    //
    // BoxedChar, BoxedInt, BoxedUnsignedInt, BoxedFloat, BoxedDouble, etc.
    // encapsulate a single variable in order to make it modifiable from Python
    // when it is used as a function parameter passed by reference or via a modifiable fixed size array.
    //
    #define _LITGEN_INSTANTIATE_BOXED_TYPE(T)                                      \
    struct Boxed##T                                                                \
    {                                                                              \
        T value;                                                                   \
        Boxed##T(T v = (T)0.) : value(v) {}                                        \
        std::string __repr__() const                                               \
        {                                                                          \
            return                                                                 \
              std::string("Boxed" #T "("                                           \
            + std::to_string(value) + ")");                                        \
        }                                                                          \
    };
    // Note: this code could not be expressed in a reasonable way as a template,
    // because the struct name is a concatenation.


    _LITGEN_INSTANTIATE_BOXED_TYPE(Char)
    _LITGEN_INSTANTIATE_BOXED_TYPE(UnsignedChar)
    _LITGEN_INSTANTIATE_BOXED_TYPE(Short)
    _LITGEN_INSTANTIATE_BOXED_TYPE(UnsignedShort)
    _LITGEN_INSTANTIATE_BOXED_TYPE(Int)
    _LITGEN_INSTANTIATE_BOXED_TYPE(UnsignedInt)
    _LITGEN_INSTANTIATE_BOXED_TYPE(Long)
    _LITGEN_INSTANTIATE_BOXED_TYPE(UnsignedLong)
    _LITGEN_INSTANTIATE_BOXED_TYPE(LongLong)
    _LITGEN_INSTANTIATE_BOXED_TYPE(UnsignedLongLong)
    _LITGEN_INSTANTIATE_BOXED_TYPE(Float)
    _LITGEN_INSTANTIATE_BOXED_TYPE(Double)
    _LITGEN_INSTANTIATE_BOXED_TYPE(LongDouble)
//}
