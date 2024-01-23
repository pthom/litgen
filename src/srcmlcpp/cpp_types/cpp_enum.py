from __future__ import annotations
import copy
from dataclasses import dataclass
from typing import Optional

from codemanip import code_utils

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.scrml_warning_settings import WarningType
from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppEnum"]


@dataclass
class CppEnum(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """

    _block: CppBlock
    enum_type: str = ""  # "class" or ""
    enum_name: str = ""
    # enum_data_type is almost always empty, but can contain the inner data type, e.g. uint32_t
    enum_data_type: str = ""

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    @property
    def block(self) -> CppBlock:
        return self._block

    @block.setter
    def block(self, value: CppBlock) -> None:
        self._block = value
        self.fill_children_parents()

    def is_enum_class(self) -> bool:
        return self.enum_type == "class"

    def name(self) -> str:
        return self.enum_name

    def str_code(self) -> str:
        r = ""
        if self.enum_type == "class":
            r += f"enum class {self.enum_name}\n"
        else:
            r += f"enum {self.enum_name}\n"
        r += "{\n"
        block_code = self.block.str_block(is_enum=True)
        r += code_utils.indent_code(block_code, indent_str=self.options.indent_cpp_str)
        r += "};\n"
        return r

    def __str__(self) -> str:
        return self.str_code()

    def __repr__(self):
        r = "enum class " if self.enum_type == "class" else "enum "
        r += self.enum_name
        return r

    def get_enum_decls(self) -> list[CppDecl]:
        r: list[CppDecl] = []
        for child in self.block.block_children:
            if isinstance(child, CppDecl):
                r.append(child)
        return r

    def get_children_with_filled_decl_values(self) -> list[CppElementAndComment]:
        children: list[CppElementAndComment] = []

        last_decl: Optional[CppDecl] = None

        for child in self.block.block_children:
            if not isinstance(child, CppDecl):
                children.append(child)
            else:
                decl = child
                decl_with_value = copy.copy(decl)

                if len(decl_with_value.initial_value_code) > 0:
                    """
                    we do not try to parse it as an integer, because sometimes an enum value
                    is a composition of other values.
                    For example: `enum Foo { A = 0, B = A << 1, C = A | B };`
                    """
                    if decl_with_value.initial_value_code in self.options.named_number_macros:
                        decl_with_value.initial_value_code = str(
                            self.options.named_number_macros[decl_with_value.initial_value_code]
                        )

                else:
                    if last_decl is None:
                        decl_with_value.initial_value_code = "0"  # in C/C++ the first value is 0 by default
                    else:
                        last_decl_value_str = last_decl.initial_value_code
                        try:
                            last_decl_value_int = int(last_decl_value_str)
                            decl_with_value.initial_value_code = str(last_decl_value_int + 1)
                        except ValueError:
                            decl.emit_warning(
                                """
                                Cannot parse the value of this enum element.
                                Hint: maybe add an entry to SrcmlcppOptions.named_number_macros""",
                                WarningType.LitgenEnumUnparsableValue,
                            )

                last_decl = decl_with_value
                children.append(decl_with_value)

        return children

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "block"):
            self.block.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
