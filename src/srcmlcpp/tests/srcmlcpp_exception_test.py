from __future__ import annotations
from codemanip import code_utils

import srcmlcpp.srcmlcpp_main
from srcmlcpp.internal.srcmlcpp_exception_detailed import SrcmlcppExceptionDetailed
from srcmlcpp.srcmlcpp_exception import SrcmlcppException
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def test_warnings():
    options = SrcmlcppOptions()
    options.flag_show_python_callstack = True
    code = "void foo(int a);"

    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code, filename="main.h")
    decl = cpp_unit.block_children[0]

    got_exception = False
    try:
        raise SrcmlcppExceptionDetailed(decl, "Artificial exception")
    except SrcmlcppException as e:
        got_exception = True
        msg = str(e)
        for part in [
            "test_warnings",
            "function_decl",
            "main.h:1:1",
            "void foo",
            "Artificial exception",
        ]:
            assert part in msg
    assert got_exception


def test_warnings_2():
    options = srcmlcpp.SrcmlcppOptions()
    code = code_utils.unindent_code(
        """
        struct __Foo
        {
            int a = 1;
        };
    """,
        flag_strip_empty_lines=True,
    )
    cpp_struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)

    msg = cpp_struct._warning_message_str("names starting with __ are reserved")
    code_utils.assert_are_codes_equal(
        msg,
        """
        Warning: names starting with __ are reserved
        While parsing a "struct", corresponding to this C++ code:
        Position:1:1
            struct __Foo
            ^
            {
                int a = 1;
    """,
    )
