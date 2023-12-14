from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base.cpp_element import CppElement
from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppUnit"]


@dataclass
class CppUnit(CppBlock):
    """A kind of block representing a full file."""

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element)

    def __str__(self) -> str:
        return self.str_block()

    def str_code(self) -> str:
        return self.str_block()

    @staticmethod
    def find_root_cpp_unit(element: CppElement) -> CppUnit:
        assert hasattr(element, "parent")  # parent should have been filled by parse_unit & CppBlock

        current = element
        while True:
            root = current
            if current.parent is None:
                break
            current = current.parent

        assert isinstance(root, CppUnit)
        return root
