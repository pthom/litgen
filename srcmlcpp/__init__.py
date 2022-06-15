"""
Interface to srcML (https://www.srcmlcpp.org/)
"""
import os, sys

_THIS_DIR = os.path.dirname(__file__)
sys.path.append("_THIS_DIR/..")

from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_exception import SrcMlException

from srcmlcpp.srcml_types import CppUnit
from srcmlcpp.srcml_main import code_to_cpp_unit, file_to_cpp_unit

from srcmlcpp.srcml_types_parse import parse_unit
from srcmlcpp.srcml_caller import srcml_to_code, code_to_srcml
