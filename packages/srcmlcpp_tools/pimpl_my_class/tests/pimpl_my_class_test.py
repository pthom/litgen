from srcmlcpp_tools import pimpl_my_class
from codemanip import code_utils


def test_simple_pimpl():
    code = """
#include "my_class.h"

#include <string>
#include <future>

// Some doc about the class, that you want to see in the header file
class MyClassPImpl
{
public:
    //
    // Some doc you also want to see in the header file, since it is in a public block
    //

    // Construct an Instance
    MyClassPImpl(const std::string& someVar)
    {
        // Some code you provide in the C++ file, but do not want to see in the header file
    }

    // Some method
    virtual bool SomeMethod() { /* ... */ }

    // Some public static method
    static bool SomeStaticMethod() { /* ... */ }

    // The destructor should not be published as is, but should use the unique_ptr default destructor
    ~MyClassPImpl() { /* ... */ }

private:
    //
    // Some private doc, which should not be published
    //

    bool SomePrivateMethod() { /* ... */ }

    std::string mSomePrivateMember;
    std::future<void> mAnoterPrivateMember;
};
    """

    result = pimpl_my_class.pimpl_my_code(code)
    # print("\n" + result.header_code)
    assert result is not None
    code_utils.assert_are_codes_equal(
        result.header_code,
        """
        class MyClassPImpl;

        // Some doc about the class, that you want to see in the header file
        class MyClass
        {
          public:
            //
            //  Some doc you also want to see in the header file, since it is in a public block
            //

            // Construct an Instance
            MyClass(const std::string & someVar);

            // Some method
            virtual bool SomeMethod();

            // Some public static method
            static bool SomeStaticMethod();


            ~MyClass();
          private:
            std::unique_ptr<MyClassPImpl> mPImpl;
        };

        """,
    )

    # print("\n" + result.glue_code)
    code_utils.assert_are_codes_equal(
        result.glue_code,
        """
        MyClass::MyClass(const std::string & someVar)
            : mPImpl(std::make_unique<MyClassPImpl>(someVar)) { }
        virtual bool MyClass::SomeMethod() {
            return mPImpl->SomeMethod(); }
        bool MyClass::SomeStaticMethod() {
            return MyClassPImpl::SomeStaticMethod(); }
        MyClass::~MyClass() = default;
        """,
    )
