"""
Defines a visitor callback type that can visit a whole tree of CppElements
"""
from __future__ import annotations
from enum import Enum
from typing import Callable

from srcmlcpp.cpp_types.base.cpp_element import CppElement


__all__ = ["CppElementsVisitorFunction", "CppElementsVisitorEvent"]


class CppElementsVisitorEvent(Enum):
    OnElement = 1  # We are visiting this element (will be raised for all elements, incl Blocks)
    OnBeforeChildren = 2  # We are about to visit a block's children
    OnAfterChildren = 3  # We finished visiting a block's children


# This defines the type of function that will visit all the Cpp Elements
# - First param: element being visited. A same element can be visited up to three times with different events
# - Second param: event (see CppElementsVisitorEvent doc)
# - Third param: depth in the source tree
CppElementsVisitorFunction = Callable[[CppElement, CppElementsVisitorEvent, int], None]
