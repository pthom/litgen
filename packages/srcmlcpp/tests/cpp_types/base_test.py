from typing import cast

from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import *


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
    assert foo2.cpp_scope().str_cpp() == "Ns"
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
          CppComment
      """,
    )
