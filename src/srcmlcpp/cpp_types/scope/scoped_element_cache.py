"""Qualifiable elements: CppElements for which we store (and cache the terse and/or qualified version)
"""
from __future__ import annotations

from srcmlcpp.cpp_types.scope import CppScope
from srcmlcpp.cpp_types.base import CppElementAndComment


CppScopeName = str


class ScopedElementCache:
    """A cache for CppElement (like CppFunctionDecl) that implement with_qualified_types() and with_terse_types()"""

    _cache: dict[CppScopeName, CppElementAndComment]

    def __init__(self) -> None:
        self._cache = {}

    def contains(self, cpp_scope: CppScope) -> bool:
        r = cpp_scope.str_cpp in self._cache.keys()
        return r

    def store(self, cpp_scope: CppScope, cpp_element: CppElementAndComment) -> None:
        self._cache[cpp_scope.str_cpp] = cpp_element

    def get(self, cpp_scope: CppScope) -> CppElementAndComment:
        assert self.contains(cpp_scope)
        r = self._cache[cpp_scope.str_cpp]
        return r

    def clear_cache(self) -> None:
        self._cache = {}
