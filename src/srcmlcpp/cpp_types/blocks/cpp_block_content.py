from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppBlockContent"]


@dataclass
class CppBlockContent(CppBlock):
    """A kind of block used by function and anonymous blocks, where the code is inside <block><block_content>
    This can be viewed as a sub-block with a different name
    """

    def __init__(self, element: SrcmlWrapper):
        super().__init__(element)

    def __str__(self) -> str:
        return self.str_block()
