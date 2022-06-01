"""
Interface to srcML (https://www.srcml.org/)
"""
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR] + sys.path


class SrcMlException(Exception):
    pass


from srcml_types import CppUnit
from srcml_main import code_to_cpp_unit, file_to_cpp_unit

from srcml_types_parse import parse_unit
from srcml_caller import srcml_to_code, code_to_srcml
