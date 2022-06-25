from dataclasses import dataclass
from typing import Union, cast

from srcmlcpp.srcml_types import *

from litgen.internal.adapted_types.adapted_class import AdaptedClass
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_enum import AdaptedEnum
from litgen.internal.adapted_types.adapted_function import AdaptedFunction
from litgen.options import LitgenOptions


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

    def __init__(self, options: LitgenOptions, block: CppBlock) -> None:
        super().__init__(options, block)
        self.adapted_elements = []
        self._fill_adapted_elements()

    # override
    def cpp_element(self) -> CppBlock:
        return cast(CppBlock, self._cpp_element)

    def _fill_adapted_elements(self) -> None:
        for child in self.cpp_element().block_children:
            if isinstance(child, CppEmptyLine):
                self.adapted_elements.append(AdaptedEmptyLine(self.options, child))
            elif isinstance(child, CppComment):
                self.adapted_elements.append(AdaptedComment(self.options, child))
            elif isinstance(child, CppStruct):
                self.adapted_elements.append(AdaptedClass(self.options, child))
            elif isinstance(child, CppFunctionDecl):
                no_class_name = ""
                is_overloaded = self.cpp_element().is_function_overloaded(child)
                self.adapted_elements.append(AdaptedFunction(self.options, child, no_class_name, is_overloaded))
            elif isinstance(child, CppEnum):
                self.adapted_elements.append(AdaptedEnum(self.options, child))
            elif isinstance(child, CppNamespace):
                self.adapted_elements.append(AdaptedNamespace(self.options, child))  # type: ignore
            elif isinstance(child, CppDeclStatement):
                emit_srcml_warning(
                    self.options.srcml_options,
                    child.srcml_xml,
                    f"Block elements of type {child.tag()} are not supported in python conversion",
                )

    # override
    def _str_stub_lines(self) -> List[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element in self.adapted_elements:
            element_lines = adapted_element._str_stub_lines()

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
            element_lines = adapted_element._str_pydef_lines()

            spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
            lines += spacing_lines

            lines += element_lines
        return lines


@dataclass
class AdaptedNamespace(AdaptedElement):
    adapted_block: AdaptedBlock

    def __init__(self, options: LitgenOptions, namespace_: CppNamespace) -> None:
        super().__init__(options, namespace_)
        self.adapted_block = AdaptedBlock(self.options, self.cpp_element().block)

    def namespace_name(self) -> str:
        return self.cpp_element().ns_name

    # override
    def cpp_element(self) -> CppNamespace:
        return cast(CppNamespace, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        # raise ValueError("To be completed")
        lines: List[str] = []

        lines.append(f"# <Namespace {self.namespace_name()}>")
        lines += self.adapted_block._str_stub_lines()
        lines.append(f"# </Namespace {self.namespace_name()}>")

        return lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        location = self.info_original_location_cpp()
        namespace_name = self.namespace_name()
        block_code_lines = self.adapted_block._str_pydef_lines()

        lines: List[str] = []
        lines.append(f"// <namespace {namespace_name}>{location}")
        lines += block_code_lines
        lines.append(f"// </namespace {namespace_name}>")
        return lines


class AdaptedUnit(AdaptedBlock):
    def __init__(self, options: LitgenOptions, unit: CppUnit):
        super().__init__(options, unit)

    # override
    def cpp_element(self) -> CppUnit:
        return cast(CppUnit, self._cpp_element)

    # override : not needed, use AdaptedBlock version
    # def _str_stub_lines(self) -> List[str]:
    #     raise ValueError("To be completed")

    # override : not needed, use AdaptedBlock version
    # def _str_pydef_lines(self) -> List[str]:
    #     raise ValueError("To be completed")
