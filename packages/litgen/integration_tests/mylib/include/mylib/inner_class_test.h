#include "mylib/api_marker.h"


namespace N
{
    struct Parent
    {
        int a = 1;
        struct Child
        {
            Child(int _b = 0): b(_b) {}
            int b = 2;
            float add(float values[3]);
        };
        Child child;

//    enum class Item
//    {
//        Zero = 0,
//        One,
//        Two
//    };
//    Item item;
    };

}
