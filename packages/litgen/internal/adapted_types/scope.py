from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class ScopeType(Enum):
    SUBMODULE = "Module"
    SUBCLASS = "Class"


@dataclass
class ScopePart:
    scope_type: ScopeType
    scope_name: str

    def pydef_scope_part_name(self) -> str:
        r = self.scope_type.value + self.scope_name
        return r


class Scope:
    scopes: List[ScopePart]

    def __init__(self, scopes: List[ScopePart] = None) -> None:
        if scopes is None:
            self.scopes = []
        else:
            self.scopes = scopes

    def concatenated_scope_names(self) -> str:
        """Name that should be used for the scope in pydef binding code"""
        scope_names = map(lambda s: s.pydef_scope_part_name(), self.scopes)
        r = "_".join(scope_names)
        return r

    def pydef_scope_name(self) -> str:
        if len(self.scopes) == 0:
            return "m"
        else:
            r = "py" + self.concatenated_scope_names()
            return r

    def scope_cpp(self) -> str:
        scope_names = map(lambda s: s.scope_name, self.scopes)
        r = "::".join(scope_names)
        return r

    def __str__(self):
        return self.scope_cpp()
