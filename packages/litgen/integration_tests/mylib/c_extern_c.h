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

#ifdef __cplusplus
}
#endif
