import srcmlcpp
from srcmlcpp.srcmlcpp_main import code_to_srcml_xml_wrapper, code_to_cpp_unit
from srcmlcpp.srcml_types import *
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp import srcmlcpp_main


def to_decl(code) -> CppDecl:
    options = SrcmlOptions()
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


def test_visitor():
    options = SrcmlOptions()
    code = code_utils.unindent_code(
        """
    namespace ns
    {
        int a = 1, b; // This will create a CppDeclStatement that will be reinterpreted as two CppDecl
        struct Foo {
            Foo();
            void foo();
        };
    }
    """,
        flag_strip_empty_lines=True,
    )
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    visit_recap = ""

    def my_visitor(element: CppElement, event: CppElementsVisitorEvent, depth: int):
        nonlocal visit_recap

        if event == CppElementsVisitorEvent.OnElement:
            type_name = type(element).__name__

            code = element.str_code_verbatim().strip()
            code_first_line = code.split("\n")[0].strip()

            info = f"{type_name} ({code_first_line})"
            visit_recap += "  " * depth + info + "\n"

    cpp_unit.visit_cpp_breadth_first(my_visitor)
    logging.warning("\n" + visit_recap)
    code_utils.assert_are_codes_equal(
        visit_recap,
        """
        CppUnit (namespace ns)
        CppNamespace (namespace ns)
        CppBlock ({)
        CppDeclStatement (int a = 1, b;)
        CppDecl (int a = 1,)
        CppType (int)
        CppDecl (b;)
        CppType ()
        CppStruct (struct Foo {)
        CppBlock ({)
        CppPublicProtectedPrivate (Foo();)
        CppConstructorDecl (Foo();)
        CppParameterList (();)
        CppFunctionDecl (void foo();)
        CppType (void)
        CppParameterList (();)
    """,
    )
