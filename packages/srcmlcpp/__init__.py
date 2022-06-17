"""
Interface to srcML (https://www.srcml.org/)
"""
import os
import sys

from srcmlcpp.srcml_caller import code_to_srcml, srcml_to_code
from srcmlcpp.srcml_exception import SrcMlException
from srcmlcpp.srcml_main import code_to_cpp_unit, file_to_cpp_unit, code_first_child_of_type
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_types import CppUnit
from srcmlcpp.srcml_types_parse import parse_unit


_THIS_DIR = os.path.dirname(__file__)
sys.path.append("_THIS_DIR/..")
