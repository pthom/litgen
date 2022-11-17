#pragma once
#include "api_marker.h"

/*

Here, we test litgen with C libraries, such a glfw:

Features:
 - Handle #ifdef __cpluscplus
    __cpluscplus should be assumed to be always true
 - Handle extern:
        extern "C" { ... }
    The code inside such a block should be parsed as if extern was not there.
 - Handle functions with a void instead of empty params:
        void foo(void)
 - unnamed params:
        void blah(int)
 - Export #define as variable
    #define GLFW_KEY_LEFT_BRACKET       91  / * [ * /
    #define GLFW_PLATFORM_ERROR         0x00010008
    etc.
*/

#ifdef __cplusplus
extern "C" {
#endif

MY_API int extern_c_add(int a, int b) { return a + b; }

MY_API int foo_void_param(void) { return 42; }

MY_API int foo_unnamed_param(int , bool, float) { return 42; }

// This is zero
#define MY_ANSWER_ZERO_COMMENTED 0 // Will be published with is comment

// Will be published with its two comments (incl this one)
#define MY_ANSWER_ONE_COMMENTED 1 // This is one


#define MY_HEXVALUE 0x43242 // Will be published
#define MY_OCTALVALUE 043242 // Will be published
#define MY_STRING "Hello" // Will be published
#define MY_FLOAT 3.14 // Will be published

#define MY_ANSWER(x) (x + 42) // Will not be published!
#define MY_DEFINE_NO_VALUE // Will not be published!
#define MY_BROKEN_FLOAT 3.14.12345 // Will not be published!
#define MY_FUNCTION_CALL f(3.14) // Will not be published!

#ifdef __cplusplus
}
#endif
