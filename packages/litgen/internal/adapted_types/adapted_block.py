from dataclasses import dataclass
from typing import Union, cast

from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp.srcml_types import *

from litgen.internal.context.litgen_context import LitgenContext
from litgen.internal.adapted_types.adapted_class import AdaptedClass
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_element import (
    AdaptedElement,
    _PROGRESS_BAR_TITLE_STUB,
    _PROGRESS_BAR_TITLE_PYDEF,
)
from litgen.internal.adapted_types.adapted_enum import AdaptedEnum
from litgen.internal.adapted_types.adapted_function import AdaptedFunction


@dataclass
class AdaptedBlock(AdaptedElement):
    adapted_elements: List[
        Union[
            AdaptedEmptyLine,
            # AdaptedDecl,        # Variable declarations are not published in the bindings
            AdaptedComment,
            AdaptedClass,
            AdaptedFunction,
            AdaptedEnum,
            # AdaptedNamespace,  # There is actually a circular dependency here (with no important consequences)
            # A Block can contain a namespace, and a namespace contains a block
        ]
    ]

    def __init__(self, lg_context: LitgenContext, block: CppBlock) -> None:
        super().__init__(lg_context, block)
        self.adapted_elements = []
        self._fill_adapted_elements()

    # override
    def cpp_element(self) -> CppBlock:
        return cast(CppBlock, self._cpp_element)

    def _fill_adapted_elements(self) -> None:
        from litgen.internal.adapted_types.adapted_namespace import AdaptedNamespace

        for child in self.cpp_element().block_children:
            if isinstance(child, CppEmptyLine):
                self.adapted_elements.append(AdaptedEmptyLine(self.lg_context, child))
            elif isinstance(child, CppComment):
                self.adapted_elements.append(AdaptedComment(self.lg_context, child))
            elif isinstance(child, CppStruct):
                is_excluded_by_name = code_utils.does_match_regex(
                    self.options.class_exclude_by_name__regex, child.class_name
                )
                if not is_excluded_by_name:
                    self.adapted_elements.append(AdaptedClass(self.lg_context, child))
            elif isinstance(child, CppFunctionDecl):
                is_excluded_by_name = code_utils.does_match_regex(
                    self.options.fn_exclude_by_name__regex, child.function_name
                )
                if not is_excluded_by_name:
                    is_overloaded = self.cpp_element().is_function_overloaded(child)
                    self.adapted_elements.append(AdaptedFunction(self.lg_context, child, is_overloaded))
            elif isinstance(child, CppEnum):
                self.adapted_elements.append(AdaptedEnum(self.lg_context, child))
            elif isinstance(child, CppNamespace):
                is_anonymous_namespace = child.ns_name == ""
                is_excluded_by_name = code_utils.does_match_regex(self.options.namespace_exclude__regex, child.ns_name)
                if not is_excluded_by_name and not is_anonymous_namespace:
                    self.adapted_elements.append(AdaptedNamespace(self.lg_context, child))  # type: ignore
            elif isinstance(child, CppDeclStatement):
                child.emit_warning(f"Block elements of type {child.tag()} are not supported in python conversion")

    # override
    def _str_stub_lines(self) -> List[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element in self.adapted_elements:
            element_lines = adapted_element._str_stub_lines()

            current_line = adapted_element.cpp_element().start().line
            global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_STUB, current_line)

            if not self.options.python_reproduce_cpp_layout:
                spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
                lines += spacing_lines

            lines += element_lines
        return lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element in self.adapted_elements:

            current_line = adapted_element.cpp_element().start().line
            global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_PYDEF, current_line)

            element_lines = adapted_element._str_pydef_lines()

            spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
            lines += spacing_lines

            lines += element_lines
        return lines
