from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import CppElement
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppSuper"]


@dataclass
class CppSuper(CppElement):
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    specifier: str = ""  # public, private or protected inheritance
    superclass_name: str = ""  # name of the super class

    def __init__(self, element: SrcmlWrapper):
        super().__init__(element)

    def str_code(self) -> str:
        if len(self.specifier) > 0:
            return f"{self.specifier} {self.superclass_name}"
        else:
            return self.superclass_name

    def __str__(self) -> str:
        return self.str_code()
