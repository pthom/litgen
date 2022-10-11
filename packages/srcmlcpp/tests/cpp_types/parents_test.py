from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import *
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


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
    options = SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    log_parents = ""

    def visitor_log_parents(cpp_element: CppElement, event: CppElementsVisitorEvent, depth: int) -> None:
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
