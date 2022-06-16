import os, sys

_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")

from codemanip import code_utils
from srcmlcpp import srcml_types_parse, srcml_main
from srcmlcpp.srcml_options import SrcmlOptions


def test_parse_cpp_decl_statement():
    options = SrcmlOptions()

    def code_to_decl_statement(code):
        element = srcml_main.get_only_child_with_tag(options, code, "decl_stmt")
        cpp_decl_statement = srcml_types_parse.parse_decl_stmt(options, element)
        cpp_decl_statement_str = str(cpp_decl_statement)
        return cpp_decl_statement

    # Basic test
    code = "int a;"
    code_utils.assert_are_equal_ignore_spaces(code_to_decl_statement(code), "int a;")

    # # Test with *, initial value and east/west const translation
    code = "int const *a=nullptr;"
    code_utils.assert_are_equal_ignore_spaces(code_to_decl_statement(code), "const int * a = nullptr;")

    # Test with several variables + modifiers
    code = "int a = 3, &b = b0, *c;"
    code_utils.assert_are_codes_equal(
        code_to_decl_statement(code),
        """
        int a = 3;
        int & b = b0;
        int * c;
    """,
    )

    # Test with double pointer, which creates a double modifier
    code = "uchar **buffer;"
    code_utils.assert_are_codes_equal(code_to_decl_statement(code), "uchar * * buffer;")

    # Test with a template type
    code = "std::map<int, std::string>x={1, 2, 3};"
    code_utils.assert_are_codes_equal(code_to_decl_statement(code), "std::map<int, std::string> x = {1, 2, 3};")

    # Test with a top comment for two decls in a decl_stmt
    code = """
    // Comment line 1
    // continued on line 2
    int a = 42, b = 0;
    """
    code_utils.assert_are_codes_equal(
        code_to_decl_statement(code),
        """
    // Comment line 1
    // continued on line 2
    int a = 42;
    // Comment line 1
    // continued on line 2
    int b = 0;
    """,
    )

    # Test with an EOL comment
    code = """
    int a = 42; // This is an EOL comment
    """
    decl = code_to_decl_statement(code)
    decl_str = str(decl)
    code_utils.assert_are_codes_equal(
        decl_str,
        """
    int a = 42; // This is an EOL comment
    """,
    )


def test_parse_function_decl():
    options = SrcmlOptions()

    def code_to_fn_decl(code):
        element = srcml_main.get_only_child_with_tag(options, code, "function_decl")
        fn_decl = srcml_types_parse.parse_function_decl(options, element)
        fn_decl_str = str(fn_decl)
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
    code_utils.assert_are_codes_equal(code_to_fn_decl(code), "double divide(int a, int b);")

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
    options = SrcmlOptions()

    def code_to_fn_decl(code):
        element = srcml_main.get_only_child_with_tag(options, code, "function")
        fn = srcml_types_parse.parse_function(options, element)
        fn_str = str(fn)
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
    options = SrcmlOptions()

    def code_to_struct_decl(code):
        element_c = srcml_main.get_only_child_with_tag(options, code, "struct")
        cpp_element = srcml_types_parse.parse_struct_or_class(options, element_c)
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
        template<typename NumericType>
        struct Point : public Object
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
    options = SrcmlOptions()

    def code_to_unit(code):
        srcml_unit = srcml_main.code_to_srcml_unit(options, code)
        cpp_element = srcml_types_parse.parse_unit(options, srcml_unit)
        cpp_element_str = str(cpp_element)
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

    cpp_element_str = code_to_unit(code)

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


def do_parse_imgui_implot(filename):
    def preprocess_imgui_code(code):
        import re

        new_code = code
        new_code = re.sub(r"IM_FMTARGS\(\d\)", "", new_code)
        new_code = re.sub(r"IM_FMTLIST\(\d\)", "", new_code)
        return new_code

    options = SrcmlOptions()
    options.code_preprocess_function = preprocess_imgui_code
    options.flag_quiet = True
    options.header_guard_suffixes.append("IMGUI_DISABLE")
    srcml_unit = srcml_main.file_to_srcml_unit(options, filename)
    unit_element = srcml_types_parse.parse_unit(options, srcml_unit)
    recomposed_code = str(unit_element)
    # logging.warning("\n" + recomposed_code)
    lines = recomposed_code.splitlines()
    assert len(lines) > 500


def test_parse_imgui():
    source_filename = os.path.realpath(_THIS_DIR + "/../../../examples_real_libs/imgui/imgui/imgui.h")
    do_parse_imgui_implot(source_filename)


def test_parse_implot():
    source_filename = os.path.realpath(_THIS_DIR + "/../../../examples_real_libs/implot/implot/implot.h")
    do_parse_imgui_implot(source_filename)
