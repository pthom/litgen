#include "mylib/api_marker.h"

// BasicEnum: a simple C-style enum
enum BasicEnum     // MY_API
{
    MyEnum_a = 1, // This is value a
    MyEnum_aa,    // this is value aa
    MyEnum_aaa,   // this is value aaa

    // Lonely comment

    // This is value b
    MyEnum_b,

    // This is c
    // with doc on several lines
    MyEnum_c = MyEnum_a | MyEnum_b,

    // MyEnum_count
};


// ClassEnumNotRegistered should not be published, as it misses the marker "// MY_API"
// By default, all enums, namespaces and classes are published,
// but you can decide to include only "marked" ones, via this litgen option:
//       options.srcml_options.api_suffixes = ["MY_API"]
//
// Note: Do not remove the empty line below, otherwise this comment would become part of
//       the enum's doc, and cause it to be registered (since it contains "MY_API")

enum class ClassEnumNotRegistered
{
    On,
    Off,
    Unknown
};


// ClassEnum: a class enum that should be published
enum class ClassEnum // MY_API
{
    On = 0,
    Off,
    Unknown
};


/*
For info, below is the python pyi stub that is published for this file:

class BasicEnum(Enum):
    """ BasicEnum: a simple C-style enum"""
    my_enum_a   # (= 1)  # This is value a
    my_enum_aa  # (= 2)  # this is value aa
    my_enum_aaa # (= 3)  # this is value aaa

    # Lonely comment

    # This is value b
    my_enum_b   # (= 4)

    # This is c
    # with doc on several lines
    my_enum_c   # (= BasicEnum.my_enum_a | BasicEnum.my_enum_b)

    # MyEnum_count


# ClassEnumNotRegistered should not be published, as it misses the marker "// MY_API"
# By default, all enums, namespaces and classes are published,
# but you can decide to include only "marked" ones, via this litgen option:
#       options.srcml_options.api_suffixes = ["MY_API"]
#
# Note: Do not remove the empty line below, otherwise this comment would become part of
#       the enum's doc, and cause it to be registered (since it contains "MY_API")



class ClassEnum(Enum):
    """ ClassEnum: a class enum that should be published"""
    on      # (= 0)
    off     # (= 1)
    unknown # (= 2)
*/
