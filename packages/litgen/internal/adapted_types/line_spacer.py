from typing import Optional

from litgen.internal.adapted_types.adapted_types import *


class LineSpacer:
    last_element: Optional[AdaptedElement] = None

    def spacing_lines(self, element: AdaptedElement, element_lines: List[str]) -> List[str]:
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

        spacing: List[str] = []

        if type_current not in handled_types:  # or type_last not in handled_types:
            spacing = []
        else:
            last_is_standout = type_last in standout_types
            current_is_standout = type_current in standout_types

            large_spacing = last_is_standout or current_is_standout
            spacing = ["", ""] if large_spacing else [""]

        self.last_element = element

        return spacing
