#include "api_marker.h"
#include <memory>
#include <vector>

// With pybind11, SmartElem is mentioned in options.class_held_as_shared__regex
// (because it might be stored as a shared_ptr in the generated code)
struct SmartElem {
    int x = 0;
};


MY_API inline std::shared_ptr<SmartElem> make_shared_elem(int x)
{
    auto r = std::make_shared<SmartElem>();
    r->x = x;
    return r;
}


class ElemContainer
{
public:
    ElemContainer():
        vec { {1}, {2}},
        shared_ptr(make_shared_elem(3)),
        vec_shared_ptrs { make_shared_elem(4), make_shared_elem(5) }
    {
    }

    std::vector<SmartElem> vec;
    std::shared_ptr<SmartElem> shared_ptr;
    std::vector<std::shared_ptr<SmartElem>> vec_shared_ptrs;
};


// The signature below is incompatible with pybind11:
//     void change_unique_elem(std::unique_ptr<Elem>& elem, int x) { ... }
// Reason: such a signature might change the pointer value! Example:
//    void reset_unique_elem(std::unique_ptr<Elem>& elem) { elem.reset(new Elem());    }
