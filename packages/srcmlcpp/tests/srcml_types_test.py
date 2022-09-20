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
    code = "int a = 1;"
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
    # logging.warning("\n" + visit_recap)
    code_utils.assert_are_codes_equal(
        visit_recap,
        """
        CppUnit (int a = 1;)
          CppDeclStatement (int a = 1;)
            CppDecl (int a = 1;)
              CppType (int)
          """,
    )


def test_parents_and_scope():
    code = """
    namespace Blah
    {
        struct Foo
        {
            enum A {
                a = 0;
            };
            void dummy();
        };
    }
    """
    options = SrcmlOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    log_parents = ""

    def visitor_log_parents(cpp_element: CppElement, event: CppElementsVisitorEvent, depth: int):
        nonlocal log_parents
        if event == CppElementsVisitorEvent.OnElement:
            assert hasattr(cpp_element, "parent")
            if cpp_element.parent is None:
                msg_parent = "None"
            else:
                msg_parent = cpp_element.parent.short_cpp_element_info()

            msg_parent = f" (parent: {msg_parent})"

            msg_scope = f" (scope: {cpp_element.cpp_scope_str()})"
            if len(cpp_element.cpp_scope_str()) == 0:
                msg_scope = " (empty scope)"

            msg = cpp_element.short_cpp_element_info() + msg_parent + msg_scope
            log_parents += "  " * depth + msg + "\n"

    cpp_unit.visit_cpp_breadth_first(visitor_log_parents)
    # print("\n" + log_parents)
    code_utils.assert_are_codes_equal(
        log_parents,
        """
        CppUnit (parent: None) (empty scope)
          CppEmptyLine (parent: CppUnit) (empty scope)
          CppNamespace name=Blah (parent: CppUnit) (empty scope)
            CppBlock (parent: CppNamespace name=Blah) (scope: Blah)
              CppStruct name=Foo (parent: CppBlock) (scope: Blah)
                CppBlock (parent: CppStruct name=Foo) (scope: Blah::Foo)
                  CppPublicProtectedPrivate (parent: CppBlock) (scope: Blah::Foo)
                    CppEnum name=A (parent: CppPublicProtectedPrivate) (scope: Blah::Foo)
                      CppBlock (parent: CppEnum name=A) (scope: Blah::Foo::A)
                        CppDecl name=a (parent: CppBlock) (scope: Blah::Foo::A)
                        CppUnprocessed (parent: CppBlock) (scope: Blah::Foo::A)
                    CppFunctionDecl name=dummy (parent: CppPublicProtectedPrivate) (scope: Blah::Foo)
                      CppType name=void (parent: CppFunctionDecl name=dummy) (scope: Blah::Foo)
                      CppParameterList (parent: CppFunctionDecl name=dummy) (scope: Blah::Foo)
          CppEmptyLine (parent: CppUnit) (empty scope)
          """,
    )
