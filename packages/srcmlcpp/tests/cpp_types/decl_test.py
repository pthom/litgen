from srcmlcpp import srcmlcpp_main
from srcmlcpp.cpp_types import *
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def to_decl(code: str) -> CppDecl:
    options = SrcmlcppOptions()
    cpp_decl = srcmlcpp_main.code_first_decl(options, code)
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
