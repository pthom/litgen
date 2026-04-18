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
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope

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
    # Per-scope replacement caches for default value translation.
    # Key: CppScope.str_cpp (e.g., "" for root, "Snippets" for a namespace).
    # The root scope ("") is also accessible as var_values_replacements_cache
    # for backward compatibility with enum registration code.
    _scoped_replacements: dict[str, ReplacementsCache]
    var_values_replacements_cache: ReplacementsCache  # alias for root scope

    # Registry of Python names defined in each non-root namespace (proxy class).
    # Used to qualify sibling references inside nested classes.
    # Key: C++ namespace name (e.g., "Snippets"), Value: set of Python names
    namespace_proxy_python_names: dict[str, set[str]]

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
        self._scoped_replacements = {}
        self.var_values_replacements_cache = self.get_scoped_replacements(CppScope([]))
        self.namespace_proxy_python_names = {}

    def clear_namespaces_code_tree(self) -> None:
        self.namespaces_stub = NamespacesCodeTree(self.options, PydefOrStub.Stub)
        self.namespaces_pydef = NamespacesCodeTree(self.options, PydefOrStub.Pydef)

    def qualified_stub_namespaces(self) -> set[CppQualifiedNamespaceName]:
        return self.namespaces_stub.qualified_namespaces()

    def unqualified_stub_namespaces(self) -> set[CppNamespaceName]:
        return self.namespaces_stub.unqualified_namespaces()

    def get_scoped_replacements(self, scope: CppScope) -> ReplacementsCache:
        """Get (or create) the ReplacementsCache for a given scope."""
        key = scope.str_cpp
        if key not in self._scoped_replacements:
            self._scoped_replacements[key] = ReplacementsCache()
        return self._scoped_replacements[key]

    def apply_scoped_var_value_replacements(self, s: str, cpp_scope: CppScope) -> str:
        """Apply var value replacements walking up the scope hierarchy.

        For scope A::B::C, applies replacements from:
        root (""), then "A", then "A::B", then "A::B::C".
        More specific scopes are applied last so they can override.
        """
        # scope_hierarchy_list is [A::B::C, A::B, A, ""] - most specific first
        # We want to apply from root to most specific, so reverse it
        for scope in reversed(cpp_scope.scope_hierarchy_list):
            key = scope.str_cpp
            if key in self._scoped_replacements:
                s = self._scoped_replacements[key].apply(s)
        return s
