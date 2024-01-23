from __future__ import annotations
from typing import cast

from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import CppNamespace, CppComment, CppFunctionDecl, CppElement, CppElementsVisitorEvent


def test_base():
    code = """
#ifndef MY_CLASS_H // this is a header guard, not filtered out

#ifdef OBSCURE_OPTIONS // This zone will be filtered out
void obscure_function();
#endif

// This is a multiline
// comment about foo
int foo() // and this is an eol comment
{
    return 42;
}

namespace Ns
{
    // This is a "function group" comment,
    // for both foo2 and foo3
    // Ns block has three children: this comment,
    // and the two functions below
    int foo2(); // eol comment for foo2
    int foo3(); // eol comment for foo3
}
#endif // #ifdef MY_CLASS_H
//"""

    options = srcmlcpp.SrcmlcppOptions()
    options.header_filter_preprocessor_regions = True
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    assert len(cpp_unit.all_functions()) == 1  # obscure_function was filtered out
    assert len(cpp_unit.all_functions_recursive()) == 3

    foo = cpp_unit.all_functions()[0]
    assert foo.cpp_element_comments.top_comment_code() == "// This is a multiline\n// comment about foo\n"
    assert foo.cpp_element_comments.eol_comment_code() == "// and this is an eol comment"

    ns = cast(CppNamespace, cpp_unit.all_elements_of_type(CppNamespace)[0])
    ns_block = ns.block

    assert len(ns_block.block_children) == 3

    comment = ns_block.block_children[0]
    assert isinstance(comment, CppComment)

    foo2 = ns_block.block_children[1]
    assert isinstance(foo2, CppFunctionDecl)
    assert foo2.cpp_scope_str() == "Ns"
    assert foo2.cpp_element_comments.top_comment_code() == ""
    # fixme: why is there a leading space.
    assert foo2.cpp_element_comments.eol_comment_code() == " // eol comment for foo2"

    assert foo2.root_cpp_unit() is cpp_unit

    overview = cpp_unit.hierarchy_overview()
    code_utils.assert_are_codes_equal(
        overview,
        """
        CppUnit
          CppEmptyLine
          CppConditionMacro name=MY_CLASS_H
          CppEmptyLine
          CppEmptyLine
          CppFunction name=foo
            CppUnprocessed
          CppEmptyLine
          CppNamespace name=Ns
            CppBlock scope=Ns
              CppComment scope=Ns
              CppFunctionDecl name=foo2 scope=Ns
                CppType name=int scope=Ns
                CppParameterList scope=Ns
              CppFunctionDecl name=foo3 scope=Ns
                CppType name=int scope=Ns
                CppParameterList scope=Ns
          CppConditionMacro
          CppComment
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
    options = srcmlcpp.SrcmlcppOptions()
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
                        CppDecl name=a scope=Blah::Foo (parent: CppBlock)
                        CppUnprocessed scope=Blah::Foo::A (parent: CppBlock)
                    CppFunctionDecl name=dummy scope=Blah::Foo (parent: CppPublicProtectedPrivate)
                      CppType name=void scope=Blah::Foo (parent: CppFunctionDecl name=dummy)
                      CppParameterList scope=Blah::Foo (parent: CppFunctionDecl name=dummy)
          CppEmptyLine (parent: CppUnit)
          """,
    )


def test_visitor():
    options = srcmlcpp.SrcmlcppOptions()
    code = "int a = 1;"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    visit_recap = ""

    def my_visitor(element: CppElement, event: CppElementsVisitorEvent, depth: int) -> None:
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
