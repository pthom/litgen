#include "api_marker.h"

#include <string>

/*
This test will exercise the following options:

    # class_expose_protected_methods__regex:
    # regex giving the list of class names for which we want to expose protected methods.
    # (by default, only public methods are exposed)
    # If set, this will use the technique described at
    # https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions)
    class_expose_protected_methods__regex: str = ""

    # class_expose_protected_methods__regex:
    # regex giving the list of class names for which we want to be able to override virtual methods
    # from python.
    # (by default, this is not possible)
    # If set, this will use the technique described at
    # https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
    #
    # Note: if you want to override protected functions, also fill `class_expose_protected_methods__regex`
    class_override_virtual_methods_in_python__regex: str = ""
 */

namespace Root
{
    namespace Inner
    {
        class MyVirtualClass
        {
        public:
            virtual ~MyVirtualClass() = default;

            MY_API std::string foo_concrete(int x, const std::string& name)
            {
                std::string r =
                      std::to_string(foo_virtual_protected(x))
                    + "_" + std::to_string(foo_virtual_public_pure())
                    + "_" + foo_virtual_protected_const_const(name);
                return r;
            }

            MY_API virtual int foo_virtual_public_pure() const = 0;
        protected:
            MY_API virtual int foo_virtual_protected(int x) const { return 42 + x; }
            MY_API virtual std::string foo_virtual_protected_const_const(const std::string& name) const {
                return std::string("Hello ") + name;
            }
        };

        // Here, we test Combining virtual functions and inheritance
        // See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#combining-virtual-functions-and-inheritance
        class MyVirtualDerivate: public MyVirtualClass
        {
        public:
            MyVirtualDerivate(): MyVirtualClass() {};
            MY_API int foo_virtual_public_pure() const override { return 53; };
            MY_API virtual int foo_derivate() { return 48; }
        };
    }
}
