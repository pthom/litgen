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


enum class ClassEnum
{
    On,
    Off,
    Unknown
};
