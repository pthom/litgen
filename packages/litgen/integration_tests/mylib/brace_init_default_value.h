#pragma once
#include <map>
#include <vector>
#include <string>
#include "api_marker.h"


struct FooBrace {
    std::vector<int> int_values = {1, 2, 3};
    std::map<std::string, int> dict_string_int{{"abc", 3}};
};


MY_API int FnBrace(FooBrace foo_brace = {}, std::vector<int> ints = {1, 2, 3})
{
    return foo_brace.int_values[0] + ints[0];
}
