"""
Types that will represent the CppElements tree parsed by srcML in an actionable way under python.

* `CppElement` is a wrapper around a srcLML xml node (it contains an exact copy of the original code)
* `CppElementAndComment` is a documented C++ element (with its comments on previous lines and at the end of line)

All elements are stored.

All declarations are stored in a corresponding object:
    * function -> CppFunction
     * struct -> CppStruct
    * enums -> CppEnum
    * etc.

Implementations (expressions, function calls, etc.) are stored as CppUnprocessed. It is still possible to retrieve their
original code.

See doc/srcml_cpp_doc.png
"""

from srcmlcpp.cpp_types.base import (
    AccessTypes,
    CppElement,
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.cpp_types.cpp_type import CppType
from srcmlcpp.cpp_types.cpp_parameter import CppParameter, CppParameterList
from srcmlcpp.cpp_types.template.cpp_template import CppTemplate
from srcmlcpp.cpp_types.blocks import CppBlock, CppBlockContent, CppPublicProtectedPrivate, CppUnit
from srcmlcpp.cpp_types.classes import CppSuper, CppSuperList, CppStruct, CppClass
from srcmlcpp.cpp_types.cpp_decl import CppDecl, CppDeclStatement
from srcmlcpp.cpp_types.cpp_enum import CppEnum
from srcmlcpp.cpp_types.functions import CppFunctionDecl, CppFunction, CppConstructorDecl, CppConstructor
from srcmlcpp.cpp_types.cpp_namespace import CppNamespace
from srcmlcpp.cpp_types.base.cpp_unprocessed import CppUnprocessed, CppEmptyLine, CppComment
from srcmlcpp.cpp_types.template.template_specialization import TemplateSpecialization, TemplateSpecializationPart
