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
original code (see str_code_verbatim())

See doc/srcml_cpp_doc.png
"""
from __future__ import annotations


from srcmlcpp.cpp_types.base import (
    CppAccessType,
    CppElement,
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)

from srcmlcpp.cpp_types.base.cpp_unprocessed import (
    CppUnprocessed,
    CppEmptyLine,
    CppComment,
)

from srcmlcpp.cpp_types.decls_types import CppType, CppDecl, CppDeclStatement

from srcmlcpp.cpp_types.functions import (
    CppParameter,
    CppParameterList,
    CppFunctionDecl,
    CppFunction,
    CppConstructorDecl,
    CppConstructor,
)

from srcmlcpp.cpp_types.template import (
    CppTemplate,
    CppTemplateSpecializationPart,
    CppTemplateSpecialization,
    CppITemplateHost,
)

from srcmlcpp.cpp_types.blocks import (
    CppBlock,
    CppBlockContent,
    CppPublicProtectedPrivate,
    CppUnit,
)

from srcmlcpp.cpp_types.cpp_enum import CppEnum

from srcmlcpp.cpp_types.classes import CppSuper, CppSuperList, CppStruct, CppClass

from srcmlcpp.cpp_types.cpp_namespace import CppNamespace

from srcmlcpp.cpp_types.scope.cpp_scope import CppScope, CppScopeType, CppScopePart

from srcmlcpp.cpp_types.cpp_define import CppDefine, CppConditionMacro

__all__ = [
    # base
    "CppAccessType",
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
    "CppDefine",
    "CppConditionMacro",
]
