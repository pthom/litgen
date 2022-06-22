"""
Interface to srcML (https://www.srcml.org/)
"""
import os
import sys

from srcmlcpp.srcml_caller import code_to_srcml, srcml_to_code
from srcmlcpp.srcml_main import code_to_cpp_unit, file_to_cpp_unit
from srcmlcpp.srcml_utils import srcml_to_str, srcml_to_str_readable
from srcmlcpp.srcml_options import SrcmlOptions


_THIS_DIR = os.path.dirname(__file__)
sys.path.append("_THIS_DIR/..")
