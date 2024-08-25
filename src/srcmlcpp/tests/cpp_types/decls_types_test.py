from __future__ import annotations
import srcmlcpp.srcmlcpp_main
from codemanip import code_utils

from srcmlcpp import srcmlcpp_main
from srcmlcpp.cpp_types import CppDecl, CppDeclStatement
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def to_decl(code: str) -> CppDecl:
    options = SrcmlcppOptions()
    cpp_decl = srcmlcpp_main.code_first_decl(options, code)
    return cpp_decl


def to_decl_statement(code: str) -> CppDeclStatement:
    options = SrcmlcppOptions()
    cpp_decl = srcmlcpp_main.code_first_decl_statement(options, code)
    return cpp_decl


def test_parse_decl_init_list():
    options = srcmlcpp.SrcmlcppOptions()

    code = "bool b {false};"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    decls = cpp_unit.all_decl_recursive()
    assert len(decls) == 1
    decl = decls[0]
    assert decl.initial_value_code == "{false}"
    assert decl.initial_value_via_initializer_list

    code = "std::vector<int> v{1, 2, 3};"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    decls = cpp_unit.all_decl_recursive()
    assert len(decls) == 1
    decl = decls[0]
    assert decl.initial_value_code == "{1, 2, 3}"
    assert decl.initial_value_via_initializer_list

    code = 'std::map<std::string, int> m {{ "a", 1}, };'  # note the final ","
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    decls = cpp_unit.all_decl_recursive()
    assert len(decls) == 1
    decl = decls[0]
    assert decl.initial_value_code == '{{ "a", 1}}'  # which is omitted here
    assert decl.initial_value_via_initializer_list


def test_is_c_string_list_ptr():
    assert to_decl("const char * const items[]").is_c_string_list_ptr()
    assert to_decl("const char * items[]").is_c_string_list_ptr()
    assert to_decl("const char ** const items").is_c_string_list_ptr()
    assert to_decl("const char ** items").is_c_string_list_ptr()

    assert not to_decl("const char ** const items=some_default_value()").is_c_string_list_ptr()
    assert to_decl("const char ** const items=nullptr").is_c_string_list_ptr()
    assert to_decl("const char ** const items=NULL").is_c_string_list_ptr()

    assert not to_decl("const char ** items[]").is_c_string_list_ptr()
    assert not to_decl("const char items[]").is_c_string_list_ptr()
    assert not to_decl("char **items").is_c_string_list_ptr()
    assert not to_decl("const unsigned char ** items").is_c_string_list_ptr()


def test_cpp_type():
    options = srcmlcpp.SrcmlcppOptions()

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "int")
    assert len(cpp_type.typenames) == 1
    assert not cpp_type.is_inferred_type()
    assert not cpp_type.is_const()

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "extern static const unsigned int**")
    assert cpp_type.is_const()
    assert cpp_type.is_static()
    assert "extern" in cpp_type.specifiers
    assert cpp_type.typenames == ["unsigned", "int"]
    assert cpp_type.modifiers == ["*", "*"]

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "static constexpr unsigned int")
    assert cpp_type.is_const()
    assert cpp_type.is_static()
    assert cpp_type.typenames == ["unsigned", "int"]

    options.functions_api_prefixes = "MY_API"
    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "MY_API int &&")
    assert "MY_API" in cpp_type.specifiers
    assert cpp_type.modifiers == ["&&"]
    assert cpp_type.typenames == ["int"]


def test_decl():
    options = srcmlcpp.SrcmlcppOptions()

    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, "int a")
    assert cpp_decl.initial_value_code == ""
    assert cpp_decl.cpp_type.str_code() == "int"

    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, "int a = 5")
    assert cpp_decl.initial_value_code == "5"

    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, "int a[5]")
    assert cpp_decl.is_c_array()
    assert cpp_decl.c_array_size_as_int() == 5
    assert cpp_decl.is_c_array()

    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, "int a[]")
    assert cpp_decl.is_c_array()
    assert cpp_decl.c_array_size_as_int() is None
    assert not cpp_decl.is_c_array_known_fixed_size()

    options.named_number_macros = {"COUNT": 3}
    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, "const int v[COUNT]")
    assert cpp_decl.is_c_array()
    assert cpp_decl.c_array_size_as_int() == 3
    assert cpp_decl.is_c_array_known_fixed_size()

    code = "unsigned int b : 3"
    cpp_decl = srcmlcpp.srcmlcpp_main.code_first_decl(options, code)
    assert cpp_decl.is_bitfield()
    assert cpp_decl.bitfield_range == ": 3"


def test_decl_statement():
    # Basic test
    code = "int a;"
    code_utils.assert_are_equal_ignore_spaces(to_decl_statement(code), "int a;")

    # # Test with *, initial value and east/west const translation
    code = "int const *a=nullptr;"
    code_utils.assert_are_equal_ignore_spaces(to_decl_statement(code), "const int * a = nullptr;")

    # Test with several variables + modifiers
    code = "int a = 3, &b = b0, *c;"
    code_utils.assert_are_codes_equal(
        to_decl_statement(code),
        """
        int a = 3;
        int & b = b0;
        int * c;
    """,
    )

    # Test with double pointer, which creates a double modifier
    code = "uchar **buffer;"
    code_utils.assert_are_codes_equal(to_decl_statement(code), "uchar * * buffer;")

    # Test with a template type
    code = "std::map<int, std::string>x={1, 2, 3};"
    code_utils.assert_are_codes_equal(to_decl_statement(code), "std::map<int, std::string> x = {1, 2, 3};")

    # Test with a top comment for two decls in a decl_stmt
    code = """
    // Comment line 1
    // continued on line 2
    int a = 42, b = 0;
    """
    code_utils.assert_are_codes_equal(
        to_decl_statement(code),
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
    decl = to_decl_statement(code)
    decl_str = str(decl)
    code_utils.assert_are_codes_equal(
        decl_str,
        """
    int a = 42; // This is an EOL comment
    """,
    )


def test_decl_qualified_type():
    code = """
        int f();
        namespace N1 {
            namespace N2 {
                struct S2 { constexpr static int s2 = 0; };
                enum class E2 { a = 0 };  // enum class!
                int f2();
            }
            namespace N3 {
                enum E3 { a = 0 };        // C enum!
                int f3();

                // We want to qualify the parameters' declarations of this function
                // Note the subtle difference for enum and enum class
                // The comment column gives the expected qualified type and initial values
                void g(
                        int _f = f(),             // => int _f = f()
                        N2::S2 s2 = N2::S2(),     // => N1::N2::S2 s2 = N1::N2::S2()
                        N2::E2 e2 = N2::E2::a,    // => N1::N2::E2 e2 = N1::N2::E2::a       (enum class)
                        E3 e3 = N3::a,            // => N1::N3::E3 a = N1::N3::a            (enum non class)
                        int _f3 = N1::N3::f3(),   // => int _f3 = N1::N3::f3()
                        int other = N1::N4::f4(), // => int other = N1::N4::f4()            (untouched!)
                        int _s2 = N2::S2::s2      // => int _s2 = N1::N2::S2::s2
                    );
            }
        }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    g = cpp_unit.all_functions_recursive()[3]

    params = g.parameter_list.parameters

    # int _f = f(),            // => int _f = f()
    i0 = params[0].decl._initial_value_code_with_qualified_types()
    assert i0 == "f()"
    t0 = params[0].decl.cpp_type.with_qualified_types().str_code()
    assert t0 == "int"

    # N2::S2 s2 = N2::S2(),    // => N1::N2::S2 s2 = N1::N2::S2()
    i1 = params[1].decl._initial_value_code_with_qualified_types()
    assert i1 == "N1::N2::S2()"
    t1 = params[1].decl.cpp_type.with_qualified_types().str_code()
    assert t1 == "N1::N2::S2"

    # N2::E2 e2 = N2::E2::a,    // => N1::N2::E2 e2 = N1::N2::E2::a (enum class)
    i2 = params[2].decl._initial_value_code_with_qualified_types()
    assert i2 == "N1::N2::E2::a"
    t2 = params[2].decl.cpp_type.with_qualified_types().str_code()
    assert t2 == "N1::N2::E2"

    # E3 e3 = N3::a,            // => N1::N3::E3 a = N1::N3::a            (enum non class)
    i3 = params[3].decl._initial_value_code_with_qualified_types()
    assert i3 == "N1::N3::a"
    t3 = params[3].decl.cpp_type.with_qualified_types().str_code()
    assert t3 == "N1::N3::E3"

    # int _f3 = N1::N3::f3(),  // => int _f3 = N1::N3::f3()
    p4 = params[4].decl.with_qualified_types().str_code()
    assert p4 == "int _f3 = N1::N3::f3()"

    # int other = N1::N4::f4() // => int other = N1::N4::f4()      (untouched!)
    p5 = params[5].decl.with_qualified_types().str_code()
    assert p5 == "int other = N1::N4::f4()"

    # int _s2 = N2::S2::s2      // => int _s2 = N1::N2::S2::s2
    p6 = params[6].decl.with_qualified_types().str_code()
    assert p6 == "int _s2 = N1::N2::S2::s2"


def test_with_qualified_types_method():
    code = """
    namespace N
    {
        S make_s_function(S s = S());
        struct S
        {
            S make_s_method(S s = S());
        };
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    fn = cpp_unit.all_functions_recursive()[0]
    method = cpp_unit.all_functions_recursive()[1]

    fn_q = fn.with_qualified_types()
    print()
    print(fn_q.str_code())
    assert fn_q.str_code() == "N::S make_s_function(N::S s = N::S());"

    method_q = method.with_qualified_types()
    print(method_q.str_code())
    assert method_q.str_code() == "N::S make_s_method(N::S s = N::S());"


def test_with_terse_types_free_function():
    code = """
            namespace N0
            {
                namespace N1
                {
                    namespace N2
                    {
                        struct S1 {};
                        struct S2 { constexpr static S1 s1 = S1(); };
                    }
                    namespace N3
                    {
                        struct S3 {};
                        void g(
                            N0::N1::N3::S3 _s31 = N0::N1::N3::S3(),
                            N1::N3::S3 _s32 = N1::N3::S3(),
                            N3::S3 _s33 = N3::S3(),
                            S3 _s34 = S3()
                        );

                        void h(
                            N0::N1::N2::S1 _s11 = N0::N1::N2::S2::s1,  // => N2::S1 _s11 = N2::S2::s1
                            N1::N2::S1 _s12 = N1::N2::S2::s1,          // => N2::S1 _s12 = N2::S2::s1
                            N2::S1 _s13 = N2::S2::s1
                        );
                    }
                }
            }
    """

    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    g = cpp_unit.all_functions_recursive()[0]
    g_terse = g.with_terse_types()
    print()
    assert g_terse.str_code() == "void g(S3 _s31 = S3(), S3 _s32 = S3(), S3 _s33 = S3(), S3 _s34 = S3());"

    h = cpp_unit.all_functions_recursive()[1]
    h_terse = h.with_terse_types()
    assert h_terse.str_code() == "void h(N2::S1 _s11 = N2::S2::s1, N2::S1 _s12 = N2::S2::s1, N2::S1 _s13 = N2::S2::s1);"


def test_with_terse_types_method():
    code = """
    namespace N
    {
        N::S make_s_function(N::S s = N::S());
        struct S
        {
            N::S make_s_method(N::S s = N::S());
        };
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    fn = cpp_unit.all_functions_recursive()[0]
    method = cpp_unit.all_functions_recursive()[1]

    fn_terse = fn.with_terse_types()
    fn_terse_str = fn_terse.str_code()
    assert fn_terse_str == "S make_s_function(S s = S());"

    # Although the method is inside an inner scope,
    # its declaration cannot yet use it (only the method body can)
    method_terse = method.with_terse_types()
    assert method_terse.str_code() == "S make_s_method(S s = S());"


def test_cpp_template_type():
    options = srcmlcpp.SrcmlcppOptions()

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "int")
    assert not cpp_type.is_template()
    assert cpp_type.template_instantiated_unique_type() is None

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::vector<int>")
    assert cpp_type.is_template()
    tpl_type = cpp_type.template_instantiated_unique_type()
    assert tpl_type is not None
    assert tpl_type.str_code() == "int"
    assert cpp_type.template_name() == "std::vector"

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::vector<int*>")
    assert cpp_type.is_template()
    tpl_type = cpp_type.template_instantiated_unique_type()
    assert tpl_type is not None
    assert tpl_type.str_code() == "int *"
    assert cpp_type.template_name() == "std::vector"

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::vector<std::pair<std::string,float>>")
    assert cpp_type.is_template()
    tpl_type = cpp_type.template_instantiated_unique_type()
    assert tpl_type is not None
    assert tpl_type.str_code() == "std::pair<std::string,float>"
    assert cpp_type.template_name() == "std::vector"

    cpp_type = srcmlcpp.srcmlcpp_main.code_to_cpp_type(options, "std::map<int, double>")
    assert cpp_type.is_template()
    assert cpp_type.template_instantiated_unique_type() is None
    assert cpp_type.template_name() == "std::map"
