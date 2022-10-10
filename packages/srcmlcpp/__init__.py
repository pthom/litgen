"""
Interface to srcML (https://www.srcml.org/)
"""

#
# 1. Types defined by this module
#

# Options
from srcmlcpp.srcml_options import SrcmlOptions

# A collection of Cpp Types (CppStruct, CppDecl, CppNamespace, etc.)
from srcmlcpp.srcml_types import *

# Exceptions produced by this module
from srcmlcpp.srcml_wrapper import SrcmlException, SrcmlExceptionDetailed

# A wrapper around the nodes of the xml tree produced by srcml
from srcmlcpp.srcml_wrapper import SrcmlWrapper

#
# 2. Main functions provided by this module
#

# code_to_cpp_unit is the main entry. It will transform code into a tree of Cpp elements
from srcmlcpp.srcmlcpp_main import code_to_cpp_unit

# code_to_srcml_xml_wrapper is a lower level utility, that returns a wrapped version of the srcML tree
from srcmlcpp.srcmlcpp_main import code_to_srcml_xml_wrapper
