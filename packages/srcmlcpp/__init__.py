"""
Interface to srcML (https://www.srcml.org/)
"""

#
# 1. Types defined by this module
#

# Options
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions

# A collection of Cpp Types (CppStruct, CppDecl, CppNamespace, etc.)
from srcmlcpp.cpp_types import *
from srcmlcpp.cpp_types import __all__ as _all_types

# Exceptions produced by this module
from srcmlcpp.srcmlcpp_exception import SrcmlcppException

# A wrapper around the nodes of the xml tree produced by srcml
from srcmlcpp.srcml_wrapper import SrcmlWrapper

#
# 2. Main functions provided by this module
#

# code_to_cpp_unit is the main entry. It will transform code into a tree of Cpp elements
from srcmlcpp.srcmlcpp_main import code_to_cpp_unit

# code_to_srcml_xml_wrapper is a lower level utility, that returns a wrapped version of the srcML tree
from srcmlcpp.srcmlcpp_main import code_to_srcml_wrapper


__all__ = [
    # Functions
    "code_to_cpp_unit",
    "code_to_srcml_wrapper",
    "SrcmlcppOptions",
    "SrcmlcppException",
    "SrcmlWrapper",
    #
    # Cpp Types
    #
    # base
    "CppAccessTypes",
    "CppElement",
    "CppElementAndComment",
    "CppElementComments",
    "CppElementsVisitorEvent",
    "CppElementsVisitorFunction",
    # cpp_unprocessed
    "CppUnprocessed",
    "CppEmptyLine",
    "CppComment",
    # decls_types
    "CppType",
    "CppDecl",
    "CppDeclStatement",
    # functions
    "CppParameter",
    "CppParameterList",
    "CppFunctionDecl",
    "CppFunction",
    "CppConstructorDecl",
    "CppConstructor",
    # classes
    "CppSuper",
    "CppSuperList",
    "CppStruct",
    "CppClass",
    # template
    "CppTemplate",
    "CppTemplateSpecializationPart",
    "CppTemplateSpecialization",
    "CppITemplateHost",
    # blocks
    "CppBlock",
    "CppBlockContent",
    "CppPublicProtectedPrivate",
    "CppUnit",
    # Scope
    "CppScope",
    "CppScopeType",
    "CppScopePart",
    # standalone
    "CppEnum",
    "CppNamespace",
]
