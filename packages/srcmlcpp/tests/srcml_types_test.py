import srcmlcpp
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
                msg_parent = cpp_element.parent.short_cpp_element_info(False)

            msg_parent = f" (parent: {msg_parent})"

            msg = cpp_element.short_cpp_element_info() + msg_parent
            log_parents += "  " * depth + msg + "\n"

    cpp_unit.visit_cpp_breadth_first(visitor_log_parents)
    # print("\n" + log_parents)
    code_utils.assert_are_codes_equal(
        log_parents,
        """
        CppUnit (parent: None)
          CppEmptyLine (parent: CppUnit)
          CppNamespace name=Blah (parent: CppUnit)
            CppBlock scope=Blah (parent: CppNamespace name=Blah)
              CppStruct name=Foo scope=Blah (parent: CppBlock)
                CppBlock scope=Blah::Foo (parent: CppStruct name=Foo)
                  CppPublicProtectedPrivate scope=Blah::Foo (parent: CppBlock)
                    CppEnum name=A scope=Blah::Foo (parent: CppPublicProtectedPrivate)
                      CppBlock scope=Blah::Foo::A (parent: CppEnum name=A)
                        CppDecl name=a scope=Blah::Foo::A (parent: CppBlock)
                        CppUnprocessed scope=Blah::Foo::A (parent: CppBlock)
                    CppFunctionDecl name=dummy scope=Blah::Foo (parent: CppPublicProtectedPrivate)
                      CppType name=void scope=Blah::Foo (parent: CppFunctionDecl name=dummy)
                      CppParameterList scope=Blah::Foo (parent: CppFunctionDecl name=dummy)
          CppEmptyLine (parent: CppUnit)
        """,
    )


def test_hierarchy_overview():
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
    overview = cpp_unit.hierarchy_overview()
    # logging.warning("\n" + overview)
    code_utils.assert_are_codes_equal(
        overview,
        """
        CppUnit
          CppEmptyLine
          CppNamespace name=Blah
            CppBlock scope=Blah
              CppStruct name=Foo scope=Blah
                CppBlock scope=Blah::Foo
                  CppPublicProtectedPrivate scope=Blah::Foo
                    CppEnum name=A scope=Blah::Foo
                      CppBlock scope=Blah::Foo::A
                        CppDecl name=a scope=Blah::Foo::A
                        CppUnprocessed scope=Blah::Foo::A
                    CppFunctionDecl name=dummy scope=Blah::Foo
                      CppType name=void scope=Blah::Foo
                      CppParameterList scope=Blah::Foo
          CppEmptyLine
    """,
    )


def test_methods():
    code = """
        struct Foo
        {
            Foo() {};
            void dummy();
        };
        void fn();
    """
    options = srcmlcpp.SrcmlOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    nb_found = 0

    def visitor_check_methods(cpp_element: CppElement, event: CppElementsVisitorEvent, depth: int):
        nonlocal nb_found
        if event == CppElementsVisitorEvent.OnElement and isinstance(cpp_element, CppFunctionDecl):
            nb_found += 1
            if cpp_element.function_name == "Foo":
                assert cpp_element.is_method()
                assert cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() == "Foo"
            if cpp_element.function_name == "dummy":
                assert cpp_element.is_method()
                assert not cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() == "Foo"
            if cpp_element.function_name == "fn":
                assert not cpp_element.is_method()
                assert not cpp_element.is_constructor()
                assert cpp_element.parent_struct_name_if_method() is None

    cpp_unit.visit_cpp_breadth_first(visitor_check_methods)

    assert nb_found == 3
