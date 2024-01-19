#include "api_marker.h"

#include <vector>

//  MyTemplateClass is a template class that will be implemented for the types ["int", "std::string"]
//
// See inside autogenerate_mylib.py:
//        options.class_template_options.add_specialization(
//            class_name_regex=r"^MyTemplateClass$",  # r".*" => all classes
//        cpp_types_list=["int", "double"],  # instantiated types
//        naming_scheme=litgen.TemplateNamingScheme.camel_case_suffix,
//        )

template<typename T>
struct MyTemplateClass
{
public:
    std::vector<T> values;

    // Standard constructor
    MyTemplateClass() {}

    // Constructor that will need a parameter adaptation
    MyTemplateClass(const T v[2]) {
        values.push_back(v[0]);
        values.push_back(v[1]);
    }

    // Standard method
    MY_API T sum()
    {
        T r = {};
        for (const auto & x: values)
            r += x;
        return r;
    }

    // Method that requires a parameter adaptation
    MY_API T sum2(const T v[2])
    {
        return sum() + v[0] + v[1];
    }
};
