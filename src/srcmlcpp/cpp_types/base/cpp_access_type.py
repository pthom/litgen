from __future__ import annotations
from enum import Enum


__all__ = ["CppAccessType"]


class CppAccessType(Enum):
    public = "public"
    protected = "protected"
    private = "private"

    @staticmethod
    def from_name(name: str) -> CppAccessType:
        if name == "public" or name == "":
            return CppAccessType.public
        elif name == "protected":
            return CppAccessType.protected
        elif name == "private":
            return CppAccessType.private
        else:
            raise AssertionError()
