import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
from litgen.internal import cpp_elements
from litgen.internal.srcml import srcml_caller, srcml_utils, srcml_comments


def test_srcml_decl_to_cpp_decl():
    pass
    # code = "int* a = 1"
    #
    # srcml_code = srcml_caller.code_to_srcml(code)
    # scrml_str = srcml_utils.srcml_to_str_readable(srcml_code)
    # logging.warning("\n" + scrml_str)
    #
    # logging.warning(srcml_utils.srcml_to_str(srcml_code))
    #
    # # x = srcml_comments.get_only_child_with_tag(code, "decl")
    # # logging.warning(x)
