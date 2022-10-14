#include "api_marker.h"


struct Copyable_ImplicitCopyCtor
{
    int a = 1;
};


struct Copyable_ExplicitCopyCtor
{
    Copyable_ExplicitCopyCtor() = default;
    Copyable_ExplicitCopyCtor(const Copyable_ExplicitCopyCtor& other): a(other.a){}
    int a = 1;
};


struct Copyable_ExplicitPrivateCopyCtor
{
    Copyable_ExplicitPrivateCopyCtor() = default;
    int a = 1;

private:
    Copyable_ExplicitPrivateCopyCtor(const Copyable_ExplicitPrivateCopyCtor& other): a(other.a){}
};


struct Copyable_DeletedCopyCtor
{
    int a = 1;
    Copyable_DeletedCopyCtor() = default;
    Copyable_DeletedCopyCtor(const Copyable_DeletedCopyCtor&) = delete;
};


namespace AAA
{
    template<typename T>
    struct Copyable_Template
    {
        T value;
    };
}
