from __future__ import annotations
from enum import Enum


__all__ = ["CppAccessTypes"]


class CppAccessTypes(Enum):
    public = "public"
    protected = "protected"
    private = "private"

    @staticmethod
    def from_name(name: str) -> CppAccessTypes:
        if name == "public" or name == "":
            return CppAccessTypes.public
        elif name == "protected":
            return CppAccessTypes.protected
        elif name == "private":
            return CppAccessTypes.private
        else:
            raise AssertionError()
