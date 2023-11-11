from __future__ import annotations
import os
from typing import cast

import srcmlcpp
from codemanip import code_utils

from srcmlcpp import cpp_types, srcmlcpp_main
from srcmlcpp.internal import cpp_types_parse
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


_THIS_DIR = os.path.dirname(__file__)


def test_parse_define():
    code = """
#define ADD(x, y) (x + y)

#define SUB(x, y) (x \
- y)

// This is zero
#define ZERO_COMMENTED 0

#define ONE_COMMENTED 1 // This is one

#define NO_VALUE /* This is a bare define */
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    cpp_defines = cpp_unit.all_cpp_elements_recursive(cpp_types.CppDefine)
    assert len(cpp_defines) == 5

    define_add = cast(cpp_types.CppDefine, cpp_defines[0])
    assert define_add.macro_name == "ADD"
    assert define_add.macro_parameters_str == "(x, y)"
    assert define_add.macro_value == "(x + y)"
    assert str(define_add) == "#define ADD(x, y) (x + y)"

    define_sub = cast(cpp_types.CppDefine, cpp_defines[1])
    assert define_sub.macro_name == "SUB"
    assert define_sub.macro_parameters_str == "(x, y)"
    assert define_sub.macro_value == "(x - y)"
    assert str(define_sub) == "#define SUB(x, y) (x - y)"

    define_zero = cast(cpp_types.CppDefine, cpp_defines[2])
    assert str(define_zero) == "#define ZERO_COMMENTED 0"
    assert define_zero.cpp_element_comments.comment_on_previous_lines == " This is zero"

    define_one = cast(cpp_types.CppDefine, cpp_defines[3])
    assert define_one.cpp_element_comments.comment_end_of_line == " This is one"

    define_no_value = cast(cpp_types.CppDefine, cpp_defines[4])
    assert not hasattr(define_no_value, "macro_value")
    assert define_no_value.cpp_element_comments.comment_end_of_line == " This is a bare define "


def test_parse_function_decl():
    options = SrcmlcppOptions()

    def code_to_fn_decl(code: str) -> str:
        element = srcmlcpp_main._tests_only_get_only_child_with_tag(options, code, "function_decl")
        fn_decl = cpp_types_parse.parse_function_decl(options, element, None)  # type: ignore
        return fn_decl.str_commented()

    # # Basic test with str
    code = "int foo();"
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), "int foo();")

    # Test with params and default values
    code = "int add(int a, int b = 5);"
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), "int add(int a, int b = 5);")

    # Test with template types and multiple spaces
    code = """
    std::vector<std::pair<size_t, int>>     enumerate(std::vector<int>&   const    xs);
    """
    code_utils.assert_are_codes_equal(
        code_to_fn_decl(code),
        "std::vector<std::pair<size_t, int>> enumerate(const std::vector<int> & xs);",
    )

    # Test with type declared after ->
    code = "auto divide(int a, int b) -> double;"
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), "auto divide(int a, int b) -> double;")

    # Test with inferred type
    code = "auto minimum(int&&a, int b = 5);"
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), "auto minimum(int && a, int b = 5);")

    # Test with top comment
    code = """
    // Comment about Foo()
    void Foo();
    """
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), code)

    # Test with eol comment
    code = "void Foo(); // Comment about Foo()"
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), code)


def test_parse_function():
    options = SrcmlcppOptions()

    def code_to_fn_decl(code: str) -> cpp_types.CppFunctionDecl:
        element = srcmlcpp_main._tests_only_get_only_child_with_tag(options, code, "function")
        fn = cpp_types_parse.parse_function(options, element, None)  # type: ignore
        return fn

    # # Basic test
    code = """
    // Apply foo
    int foo() { return 42; }
    """
    code_utils.assert_are_codes_equal(
        code_to_fn_decl(code),
        """
        // Apply foo
        int foo()
        <unprocessed_block/>
    """,
    )


def test_parse_struct():
    options = SrcmlcppOptions()

    def code_to_struct_decl(code: str) -> str:
        element_c = srcmlcpp_main._tests_only_get_only_child_with_tag(options, code, "struct")
        cpp_element = cpp_types_parse.parse_struct_or_class(options, element_c, None)  # type: ignore
        cpp_element_str = str(cpp_element)
        # logging.warning("\n" + cpp_element_str)
        return cpp_element_str

    code = """
    // A somewhat contrived example
    // of a templated Point structure
    template<typename NumericType> struct Point: public Object
    {
        // coordinates
        NumericType x = NumericType{}, y = NumericType{};

        // Constructor from coordinates
        Point(T _x, T _y): x(_x), y(_y)  {}
        Point();  // default constructor

        T getX();
        T getY(); // get y
        T getZ();

        //
        // Norms: we provide
        //    * Norm2
        //    * NormManhattan
        //

        T Norm2();          // this is the euclidean norm
        T NormManhattan() { return fabs(x) + fabs(y);}  // this is the manhattan norm

        friend class Serializer;

    private:
        void Foo(); // A method that shall not be published
        T x_old, y_old; // some members that shall not be published
    };
    """

    cpp_element_str = code_to_struct_decl(code)

    expected_code = """
        // A somewhat contrived example
        // of a templated Point structure
        template<typename NumericType> struct Point : public Object
        {
        public: // <default_access_type/>
            // coordinates
            NumericType x = NumericType{};
            // coordinates
            NumericType y = NumericType{};

            // Constructor from coordinates
            Point(T _x, T _y)<unprocessed_block/>
            Point() // default constructor

            T getX();
            T getY(); // get y
            T getZ();

            //
            //  Norms: we provide
            //     * Norm2
            //     * NormManhattan
            //

            T Norm2(); // this is the euclidean norm
            T NormManhattan()<unprocessed_block/> // this is the manhattan norm

            <unprocessed_friend/>

        private:
            void Foo(); // A method that shall not be published
            T x_old; // some members that shall not be published
            T y_old; // some members that shall not be published
        };
    """

    code_utils.assert_are_codes_equal(cpp_element_str, expected_code)


def test_parse_unit():
    options = SrcmlcppOptions()
    options.header_filter_preprocessor_regions = True

    def code_to_unit_str(code: str) -> str:
        cpp_unit = srcmlcpp_main.code_to_cpp_unit(options, code)
        cpp_element_str = str(cpp_unit)
        # logging.warning("\n" + cpp_element_str)
        return cpp_element_str

    code = """
    #ifndef MY_API_H
    #define MY_API_H

    namespace MyApi
    {
        #ifdef SOME_OPTION
        void Foo(); // Foo() !
        #endif

        // Foo class
        class FooStruct
        {
            int mA, mB;
        public:
            // Constructor with a and b
            FooStruct(int a, int b) : mA(a), mB(b) {}

            int add(int x)  { return mA + mB + x; } // an addition
        };

        enum FooEnum
        {
            FooEnum_A = 1, // A Value
            FooEnum_B,
            FooEnum_C,
            FooEnum_Count  // Count nb of elements
        };

        enum class FooEnum2
        {
            A = 1,
            B,
            C,
            Count
        };
    } // namespace MyApi
    namespace MyApi2
    {
        void Foo2();
    }
    #endif // #ifndef MY_API_H
    """

    cpp_element_str = code_to_unit_str(code)

    expected_code = """
        #ifndef MY_API_H
        #define MY_API_H

        namespace MyApi
        {

            // Foo class
            class FooStruct
            {
            private: // <default_access_type/>
                int mA;
                int mB;
            public:
                // Constructor with a and b
                FooStruct(int a, int b)<unprocessed_block/>

                int add(int x)<unprocessed_block/> // an addition
            };

            enum FooEnum
            {
                FooEnum_A = 1, // A Value
                FooEnum_B,
                FooEnum_C,
                FooEnum_Count // Count nb of elements
            };

            enum class FooEnum2
            {
                A = 1,
                B,
                C,
                Count
            };
        } // namespace MyApi
        namespace MyApi2
        {
            void Foo2();
        }
        #endif
    """

    code_utils.assert_are_codes_equal(cpp_element_str, expected_code)


def do_parse_imgui_implot(filename: str) -> None:
    def preprocess_imgui_code(code):
        import re

        new_code = code
        new_code = re.sub(r"IM_FMTARGS\(\d\)", "", new_code)
        new_code = re.sub(r"IM_FMTLIST\(\d\)", "", new_code)
        return new_code

    options = SrcmlcppOptions()
    options.code_preprocess_function = preprocess_imgui_code
    options.flag_quiet = True
    options.header_filter_acceptable__regex += "|^IMGUI_DISABLE$"
    cpp_unit = srcmlcpp_main.code_to_cpp_unit(options, filename=filename)
    recomposed_code = str(cpp_unit)
    # logging.warning("\n" + recomposed_code)
    lines = recomposed_code.splitlines()
    assert len(lines) > 500


def disabled_test_parse_imgui():
    """
    Disabled because too slow (about 20 seconds). Handle this in a later profiling session
    """
    source_filename = os.path.realpath(_THIS_DIR + "../../../../../lg_projects/lg_imgui/external/imgui/imgui.h")
    do_parse_imgui_implot(source_filename)


def disabled_test_parse_implot():
    source_filename = os.path.realpath(_THIS_DIR + "../../../../../lg_projects/imgui_bundle/external/implot/implot.h")
    do_parse_imgui_implot(source_filename)
