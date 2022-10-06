#include "mylib/api_marker.h"

#include <stdio.h>
#include <vector>
#include <string>


// This is the class doc. It will be published as MyClass.__doc__
// The "// MY_API" comment after the class decl indicates that this class will be published.
// it is necessary, since `options.srcml_options.api_suffixes = "MY_API"`
// was set inside autogenerate_mylib.py
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

    // unpublished_calc: this function should not be published (no MY_API marker)
    int unpublished_calc(int x) { return x * factor + delta + 3;}

    ///////////////////////////////////////////////////////////////////////////
    // Static method
    ///////////////////////////////////////////////////////////////////////////

    // Returns a static message
    MY_API static std::string static_message() { return std::string("Hi!"); }
};


// StructNotRegistered should not be published, as it misses the marker "// MY_API"
// By default, all enums, namespaces and classes are published,
// but you can decide to include only "marked" ones, via this litgen option:
//       options.srcml_options.api_suffixes = "MY_API"
//
// Note: Do not remove the empty line below, otherwise this comment would become part of
//       the enum's doc, and cause it to be registered (since it contains "MY_API")

struct StructNotRegistered
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

    MY_API static MySingletonClass& instance() // return_value_policy::reference
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


struct MyFinalClass final
{
    MY_API int foo() { return 42; };
};
