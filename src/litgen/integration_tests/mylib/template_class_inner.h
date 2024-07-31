#include "api_marker.h"

#include <vector>

//  Pair is a template class with an inner struct DataContainer
//  that will be implemented for the types ["int", "std::string"]
//
// See inside autogenerate_mylib.py:
//    options.class_template_options.add_specialization(
//        name_regex=r"^Pair$",  # r".*" => all classes
//    cpp_types_list_str=["int", "std::string"],  # instantiated types
//    cpp_synonyms_list_str=[],
//    )

#include <array>

template<typename DataType>
struct Pair
{
    struct DataContainer
    {
        DataType value;
    };
    DataContainer first, second;
};
