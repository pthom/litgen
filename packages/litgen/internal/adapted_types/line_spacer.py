from __future__ import annotations
from typing import Optional

from litgen.internal.adapted_types.adapted_class import (
    AdaptedClass,
    AdaptedClassMember,
)
from litgen.internal.adapted_types.adapted_comment import AdaptedComment
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_enum import (
    AdaptedEnum,
    AdaptedEnumDecl,
)
from litgen.internal.adapted_types.adapted_function import AdaptedFunction
from litgen.internal.adapted_types.adapted_namespace import AdaptedNamespace
from litgen.options import LitgenOptions


class LineSpacerCpp:
    last_element: Optional[AdaptedElement] = None

    def spacing_lines(self, element: AdaptedElement, element_lines: list[str]) -> list[str]:
        if len(element_lines) == 0:
            return []
        if self.last_element is None:
            self.last_element = element
            return []

        normal_types = [AdaptedFunction, AdaptedDecl]
        standout_types = [AdaptedEnum, AdaptedClass, AdaptedNamespace]
        handled_types = normal_types + standout_types

        type_last = type(self.last_element)
        type_current = type(element)

        spacing: list[str] = []

        if type_current not in handled_types:  # or type_last not in handled_types:
            spacing = []
        else:
            last_is_standout = type_last in standout_types
            current_is_standout = type_current in standout_types

            large_spacing = last_is_standout or current_is_standout
            spacing = ["", ""] if large_spacing else [""]

        self.last_element = element

        return spacing


class LineSpacerPython:
    options: LitgenOptions
    last_element: Optional[AdaptedElement] = None

    def __init__(self, options: LitgenOptions):
        self.options = options

    def spacing_lines(self, element: AdaptedElement, element_lines: list[str]) -> list[str]:
        if self.options.python_reproduce_cpp_layout:
            return []
        if len(element_lines) == 0:
            return []
        if self.last_element is None:
            self.last_element = element
            return []

        types_space_one_line = [AdaptedFunction, AdaptedDecl]
        if not self.options.python_reproduce_cpp_layout:
            types_space_one_line.append(AdaptedComment)

        types_space_two_lines = [AdaptedEnum, AdaptedClass, AdaptedNamespace]
        handled_types = types_space_one_line + types_space_two_lines

        type_last = type(self.last_element)
        type_current = type(element)

        spacing: list[str] = []
        if (
            (type_current == AdaptedEnumDecl or type_current == AdaptedClassMember)
            and type_last == AdaptedComment
            and not self.options.python_reproduce_cpp_layout
        ):
            spacing = [""]
        elif type_current not in handled_types:  # or type_last not in handled_types:
            spacing = []
        else:
            last_is_standout = type_last in types_space_two_lines
            current_is_standout = type_current in types_space_two_lines

            large_spacing = last_is_standout or current_is_standout
            spacing = ["", ""] if large_spacing else [""]

        self.last_element = element

        return spacing
