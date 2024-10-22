#pragma once
#include <map>
#include <vector>
#include <string>
#include "api_marker.h"


struct FooBrace {
    std::vector<int> int_values = {1, 2, 3};
    std::map<std::string, int> dict_string_int{{"abc", 3}};
};


// Must be last in the generation (see explanation inside test_change_decl_stmt_to_function_decl_if_suspicious)
MY_API int FnBrace(FooBrace foo_brace = {}, std::vector<int> ints = {1, 2, 3})
{
    return foo_brace.int_values[0] + ints[0];
}
