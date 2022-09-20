from enum import Enum
from dataclasses import dataclass
from typing import List


class CppScopeType(Enum):
    Namespace = "Namespace"
    ClassOrStruct = "ClassOrStruct"
    Enum = "Enum"


@dataclass
class CppScopePart:
    scope_type: CppScopeType
    scope_name: str


class CppScope:
    scope_parts: List[CppScopePart]

    def __init__(self, scopes: List[CppScopePart] = None) -> None:
        if scopes is None:
            self.scope_parts = []
        else:
            self.scope_parts = scopes

    def str_cpp(self) -> str:
        """ "Returns this scope as a cpp prefix, e.g Foo::Blah"""
        if len(self.scope_parts) == 0:
            return ""
        scope_names = map(lambda s: s.scope_name, self.scope_parts)
        r = "::".join(scope_names)
        return r

    def __str__(self):
        return self.str_cpp()
