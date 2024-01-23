from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import CppElementComments
from srcmlcpp.cpp_types.classes.cpp_struct import CppStruct
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppClass"]


@dataclass
class CppClass(CppStruct):
    """
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def __str__(self) -> str:
        return self.str_commented()

    def __repr__(self):
        r = "class " + self.class_name
        return r
