import srcmlcpp.srcmlcpp_main
from codemanip import code_utils

from srcmlcpp import srcmlcpp_main
from srcmlcpp.cpp_types import *
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def to_decl(code: str) -> CppDecl:
    options = SrcmlcppOptions()
    cpp_decl = srcmlcpp_main.code_first_decl(options, code)
    return cpp_decl


def to_decl_statement(code: str) -> CppDeclStatement:
    options = SrcmlcppOptions()
    cpp_decl = srcmlcpp_main.code_first_decl_statement(options, code)
    return cpp_decl


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
