// A super nice enum for demo purposes
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
//       ClassEnumNotRegistered's doc, and cause it to be registered (since it contains "MY_API")

enum class ClassEnumNotRegistered
{
    On,
    Off,
    Unknown
};


// This enum should be published
enum class ClassEnum // MY_API
{
    On,
    Off,
    Unknown
};
