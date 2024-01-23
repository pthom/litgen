from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Final, Optional


class CppScopeType(Enum):
    Namespace = "Namespace"
    ClassOrStruct = "ClassOrStruct"
    Enum = "Enum"
    _Unknown = "_Unknown"


@dataclass
class CppScopePart:
    scope_type: CppScopeType
    scope_name: str


class CppScope:
    scope_parts: Final[list[CppScopePart]]

    def __init__(self, scopes: list[CppScopePart]) -> None:
        self.scope_parts = scopes

    @staticmethod
    def from_string(s: str) -> CppScope:
        scope_strs = s.split("::")
        scope_parts = [CppScopePart(CppScopeType._Unknown, scope_str) for scope_str in scope_strs]
        r = CppScope(scope_parts)
        return r

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CppScope):
            return NotImplemented
        return self.str_cpp() == other.str_cpp()

    def parent_scope(self) -> CppScope | None:
        if len(self.scope_parts) == 0:
            return None
        new_scope_parts = copy.deepcopy(self.scope_parts[:-1])
        return CppScope(new_scope_parts)

    def scope_hierarchy_list(self) -> list[CppScope]:
        """Given "A::B::C", return ["A::B::C", "A::B", "A", ""]"""
        r = []
        current_scope: Optional[CppScope] = self
        while current_scope is not None:
            r.append(current_scope)
            current_scope = current_scope.parent_scope()
        return r

    def can_access_scope(self, other_scope: CppScope) -> bool:
        parent: CppScope | None = self
        while parent is not None:
            if parent == other_scope:
                return True
            parent = parent.parent_scope()
        return False

    def str_cpp(self) -> str:
        """Returns this scope as a cpp scope, e.g Foo::Blah"""
        if len(self.scope_parts) == 0:
            return ""
        scope_names = map(lambda s: s.scope_name, self.scope_parts)
        r = "::".join(scope_names)
        return r

    def str_cpp_prefix(self) -> str:
        """Returns this scope as a cpp prefix, e.g Foo::Blah::"""
        s = self.str_cpp()
        if len(s) == 0:
            return ""
        else:
            return s + "::"

    def qualified_name(self, name: str) -> str:
        return self.str_cpp_prefix() + name

    def __str__(self):
        return self.str_cpp()

    def __repr__(self):
        return self.str_cpp()

    def __hash__(self) -> int:
        return hash(self.str_cpp())
