// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/mylib_main/mylib.h                                                               //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include "api_marker.h"

//#include "mylib/basic_test.h"
//#include "mylib/header_filter_test.h"
//#include "mylib/c_style_array_test.h"
//#include "mylib/c_style_buffer_to_pyarray_test.h"
//#include "mylib/c_string_list_test.h"
//#include "mylib/modifiable_immutable_test.h"
//#include "mylib/overload_test.h"
//#include "mylib/enum_test.h"
//#include "mylib/class_test.h"
//#include "mylib/class_inheritance_test.h"
//#include "mylib/class_adapt_test.h"
//#include "mylib/class_copy_test.h"
//#include "mylib/class_virtual_test.h"
//#include "mylib/return_value_policy_test.h"
//#include "mylib/inner_class_test.h"
//#include "mylib/mix_adapters_class_test.h"
//#include "mylib/namespace_test.h"
//#include "mylib/operators.h"
//#include "mylib/call_policies_test.h"
//#include "mylib/qualified_scoping_test.h"
//#include "mylib/template_function_test.h"
//#include "mylib/template_class_test.h"
//#include "mylib/c_extern_c.h"
//#include "mylib/class_default_ctor_test.h"
//#include "mylib/brace_init_default_value.h"

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/template_class_inner.h included by mylib/mylib_main/mylib.h                      //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/mylib_main/mylib.h continued                                                     //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//#include "mylib/sandbox.h"
