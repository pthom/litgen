import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import litgen.internal.srcml as srcml
import litgen.internal.code_utils as code_utils


def truc():
    code = """
    enum Foo {
        a = 1, // A value
        b = 2, // B Value
        c // End
    };
    """

    srcml_element = srcml.code_to_srcml(code, encoding="utf-8")
    print(srcml.srcml_to_code(srcml_element, encoding="utf-8"))

    print(srcml.srcml_to_str_readable(srcml_element))

# truc()

