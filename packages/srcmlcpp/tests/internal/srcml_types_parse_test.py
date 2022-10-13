import os

from codemanip import code_utils

from srcmlcpp import cpp_types, srcmlcpp_main
from srcmlcpp.internal import cpp_types_parse
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


_THIS_DIR = os.path.dirname(__file__)


def test_parse_function_decl():
    options = SrcmlcppOptions()

    def code_to_fn_decl(code: str) -> cpp_types.CppFunctionDecl:
        element = srcmlcpp_main._tests_only_get_only_child_with_tag(options, code, "function_decl")
        fn_decl = cpp_types_parse.parse_function_decl(options, element)
        return fn_decl

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
        fn = cpp_types_parse.parse_function(options, element)
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
        cpp_element = cpp_types_parse.parse_struct_or_class(options, element_c)
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
        public:// <default_access_type/>
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
        <unprocessed_define/>

        namespace MyApi
        {

            // Foo class
            class FooStruct
            {
            private:// <default_access_type/>
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
    source_filename = os.path.realpath(
        _THIS_DIR + "../../../../../lg_projects/lg_imgui_bundle/external/implot/implot.h"
    )
    do_parse_imgui_implot(source_filename)
