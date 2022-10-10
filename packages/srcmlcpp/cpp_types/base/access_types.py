from __future__ import annotations
from enum import Enum


__all__ = ["AccessTypes"]


class AccessTypes(Enum):
    public = "public"
    protected = "protected"
    private = "private"

    @staticmethod
    def from_name(name: str) -> AccessTypes:
        if name == "public" or name == "":
            return AccessTypes.public
        elif name == "protected":
            return AccessTypes.protected
        elif name == "private":
            return AccessTypes.private
        else:
            raise AssertionError()
