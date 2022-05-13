#pragma once

#ifndef MY_API
#define MY_API
#endif

namespace LiterateGeneratorExample
{
    // Adds two numbers
    MY_API int add(int a, int b) { return a + b; }

    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

} // namespace LiterateGeneratorExample