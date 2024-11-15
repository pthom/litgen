from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from litgen.internal.context.namespaces_code_tree import (
    NamespacesCodeTree,
    PydefOrStub,
)
from litgen.internal.context.replacements_cache import ReplacementsCache
from litgen.internal.context.type_synonyms import CppTypeName
from litgen.internal.context.type_synonyms import CppNamespaceName, CppQualifiedNamespaceName
from srcmlcpp.cpp_types.cpp_enum import CppEnum

if TYPE_CHECKING:
    from litgen.options import LitgenOptions


@dataclass
class LitgenContext:
    """
    This context store the options, as well as some infos on the encountered types and namespace
    for post-process generation.
    """

    options: LitgenOptions
    encountered_cpp_boxed_types: set[CppTypeName]
    encountered_cpp_enums: list[CppEnum]
    namespaces_stub: NamespacesCodeTree
    namespaces_pydef: NamespacesCodeTree
    var_values_replacements_cache: ReplacementsCache

    # cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions
    protected_methods_glue_code: str = ""
    # cf https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
    virtual_methods_glue_code: str = ""

    current_parsed_filename: str = ""

    def __init__(self, options: LitgenOptions):
        self.options = options
        self.encountered_cpp_boxed_types = set()
        self.encountered_cpp_enums = []
        self.namespaces_stub = NamespacesCodeTree(self.options, PydefOrStub.Stub)
        self.namespaces_pydef = NamespacesCodeTree(self.options, PydefOrStub.Pydef)
        self.var_values_replacements_cache = ReplacementsCache()

    def clear_namespaces_code_tree(self) -> None:
        self.namespaces_stub = NamespacesCodeTree(self.options, PydefOrStub.Stub)
        self.namespaces_pydef = NamespacesCodeTree(self.options, PydefOrStub.Pydef)

    def qualified_stub_namespaces(self) -> set[CppQualifiedNamespaceName]:
        return self.namespaces_stub.qualified_namespaces()

    def unqualified_stub_namespaces(self) -> set[CppNamespaceName]:
        return self.namespaces_stub.unqualified_namespaces()
