# pyright: reportAttributeAccessIssue=false
from __future__ import annotations
import os
import sys

from codemanip import code_utils

import srcmlcpp
from srcmlcpp.internal import code_to_srcml


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_srcml_to_str_readable():
    code = """
// A superb struct
struct Foo
{
    Foo(int x) : mX(x) {}
    int mX = 0;
private:
    void Priv();
};
"""

    code_xml = code_to_srcml.code_to_srcml(code)
    code_info = srcmlcpp.internal.srcml_utils.srcml_to_str_readable(code_xml)

    expected_code_info = """unit
    comment text="// A superb struct"                       line  2
    struct text="struct"                                    lines 3-9
        name text="Foo"                                     line  3
        block text="{"                                      lines 4-9
            public                                          lines 5-7
                constructor                                 line  5
                    name text="Foo"
                    parameter_list text="("
                        parameter
                            decl
                                type
                                    name text="int"
                                name text="x"
                    member_init_list text=":"
                        call
                            name text="mX"
                            argument_list text="("
                                argument
                                    expr
                                        name text="x"
                    block text="{"
                        block_content
                decl_stmt                                   line  6
                    decl
                        type
                            name text="int"
                        name text="mX"
                        init text="="
                            expr
                                literal text="0"
            private text="private:"                         lines 7-8
                function_decl                               line  8
                    type
                        name text="void"
                    name text="Priv"
                    parameter_list text="()"
"""

    code_utils.assert_are_codes_equal(code_info, expected_code_info)
