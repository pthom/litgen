#include "api_marker.h"

#include <stdio.h>
#include <vector>
#include <string>


// This is the class doc. It will be published as MyClass.__doc__
class MyClass
{
public:
    MyClass(int factor = 10, const std::string& message = "hello"): factor(factor), message(message) {}
    ~MyClass() {}


    ///////////////////////////////////////////////////////////////////////////
    // Simple struct members
    ///////////////////////////////////////////////////////////////////////////
    int factor = 10, delta = 0;
    std::string message;


    ///////////////////////////////////////////////////////////////////////////
    // Stl container members
    ///////////////////////////////////////////////////////////////////////////

    // By default, modifications from python are not propagated to C++ for stl containers
    // (see https://pybind11.readthedocs.io/en/stable/advanced/cast/stl.html)
    std::vector<int> numbers;
    // However you can call dedicated modifying methods
    MY_API void append_number_from_cpp(int v) { numbers.push_back(v); }


    ///////////////////////////////////////////////////////////////////////////
    // Fixed size *numeric* array members
    //
    // They will be published as a py::array, and modifications will be propagated
    // on both sides transparently.
    ///////////////////////////////////////////////////////////////////////////

    int values[2] = {0, 1};
    bool flags[3] = {false, true, false};
    // points is a fixed size array, but not of a numeric type. It will *not* be published!
    Point2 points[2];

    static const int const_static_value = 101;
    static int static_value;

    ///////////////////////////////////////////////////////////////////////////
    // Simple methods
    ///////////////////////////////////////////////////////////////////////////

    // calc: example of simple method
    MY_API int calc(int x) { return x * factor + delta; }
    // set_message: another example of simple method
    MY_API void set_message(const std::string & m) { message = m;}

    // unpublished_method: this function should not be published (no MY_API marker)
    int unpublished_method(int x) { return x * factor + delta + 3;}

    ///////////////////////////////////////////////////////////////////////////
    // Static method
    ///////////////////////////////////////////////////////////////////////////

    // Returns a static message
    MY_API static std::string static_message() { return std::string("Hi!"); }
};


// Struct_Detail should not be published, as the options exclude classes whose name end in "Detail".
// See this line in autogenerate_mylib.py:
//      options.class_exclude_by_name__regex = "Detail$"
struct Struct_Detail
{
    int a = 0;
};


// MySingletonClass: demonstrate how to instantiate a singleton
// - The instance method shall return with return_value_policy::reference
// - The destructor may be private
class MySingletonClass
{
public:
    int value = 0;
    MySingletonClass() = default;

    // see: options.fn_return_force_policy_reference_for_references__regex = r"instance"
    MY_API static MySingletonClass& instance()
    {
        static MySingletonClass instance;
        return instance;
    }
private:
    // For a singleton class, the destructor is typically private
    // This will be mentioned in the pydef code:
    // see https://pybind11.readthedocs.io/en/stable/advanced/classes.html#non-public-destructors
    ~MySingletonClass() {}
};


const int MyClass::const_static_value;
int MyClass::static_value = 102;


// This struct is final, and thus cannot be inherited from python
struct MyFinalClass final
{
    MY_API int foo() { return 42; };
};


// This class accepts dynamic attributes
// see autogenerate_mylib.py:
//     options.class_dynamic_attributes__regex = r"Dynamic$"
struct MyStructDynamic
{
    int cpp_member = 1;
};


struct MyStructWithNestedEnum
{
    enum class Choice { A = 0 };
    // The first param of this function uses the inner scope of this class!
    // When building the bindings, we need to add MyStructWithNestedEnum::
    MY_API int HandleChoice(Choice value = Choice::A) { return 0; }
};
