#include "mylib/api_marker.h"

// BasicEnum: a simple C-style enum
enum BasicEnum
{
    // C-style enums often contain a prefix that is the enum name in itself, in order
    // not to pollute the parent namespace.
    // Since enum members do not leak to the parent namespace in python, litgen will remove the prefix by default.

    BasicEnum_a = 1, // This will be exported as BasicEnum.a
    BasicEnum_aa,    // This will be exported as BasicEnum.aa
    BasicEnum_aaa,   // This will be exported as BasicEnum.aaa

    // Lonely comment

    // This is value b
    BasicEnum_b,

    BasicEnum_count // By default this "count" item is not exported: see options.enum_flag_skip_count
};


// ClassEnumNotRegistered should not be published, as it misses the marker "// MY_API"
// By default, all enums, namespaces and classes are published,
// but you can decide to include only "marked" ones, via this litgen option:
//       options.srcml_options.api_suffixes = "MY_API"
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
enum class ClassEnum
{
    On = 0,
    Off,
    Unknown
};


/*
For info, below is the python pyi stub that is published for this file:

class BasicEnum(Enum):
    """ BasicEnum: a simple C-style enum"""

    a   # (= 1)  # This will be exported as BasicEnum.a
    aa  # (= 2)  # This will be exported as BasicEnum.aa
    aaa # (= 3)  # This will be exported as BasicEnum.aaa

    # Lonely comment

    # This is value b
    b   # (= 4)

    # This is c
    # with doc on several lines
    c   # (= BasicEnum.a | BasicEnum.b)


class ClassEnum(Enum):
    """ ClassEnum: a class enum that should be published"""
    on      # (= 0)
    off     # (= 1)
    unknown # (= 2)
*/
