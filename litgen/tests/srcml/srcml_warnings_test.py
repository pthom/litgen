import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/../.."] + sys.path

from litgen.internal import srcml
import litgen


def test_warnings():
    options = litgen.code_style_imgui()
    old_flag_show_python_callstack = litgen.LITGEN_OPTIONS.flag_show_python_callstack
    litgen.LITGEN_OPTIONS.flag_show_python_callstack = True
    code = "void foo(int a);"

    cpp_unit = srcml.code_to_cpp_unit(options, code, filename="main.h")
    decl = cpp_unit.block_children[0]

    got_exception = False
    try:
        raise srcml.SrcMlException(decl.srcml_element, "Artificial exception")
    except srcml.SrcMlException as e:
        got_exception = True
        msg = str(e)
        for part in ["test_warning", "function_decl", "main.h:1:1", "void foo", "Artificial exception"]:
            assert part in msg
    assert got_exception == True

    litgen.LITGEN_OPTIONS.flag_show_python_callstack = old_flag_show_python_callstack
