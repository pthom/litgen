from __future__ import annotations
from dataclasses import dataclass
from typing import Union, cast

from codemanip import code_replacements

from srcmlcpp.srcml_types import *

from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.options import LitgenOptions


@dataclass
class AdaptedEnumDecl(AdaptedDecl):
    enum_parent: AdaptedEnum

    def __init__(self, options: LitgenOptions, decl: CppDecl, enum_parent: AdaptedEnum) -> None:
        self.enum_parent = enum_parent
        super().__init__(options, decl)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_name_cpp_decorated(self) -> str:
        is_class_enum = self.enum_parent.cpp_element().enum_type == "class"
        decl_name_cpp = self.cpp_element().decl_name
        if not is_class_enum:
            return decl_name_cpp
        else:
            r = self.enum_parent.cpp_element().enum_name + "::" + decl_name_cpp
            return r

    def decl_name_python(self) -> str:
        decl_name_cpp = self.cpp_element().decl_name
        decl_name_python = cpp_to_python.enum_value_name_to_python(
            self.options, self.enum_parent.cpp_element(), self.cpp_element()
        )
        return decl_name_python

    def decl_value_python(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        decl_value_python = cpp_to_python.var_value_to_python(self.options, decl_value_cpp)
        #
        # Sometimes, enum decls have interdependent values like this:
        #     enum MyEnum {
        #         MyEnum_a = 1, MyEnum_b,
        #         MyEnum_foo = MyEnum_a | MyEnum_b    //
        #     };
        #
        # So, we search and replace enum strings in the default value (.init)
        #
        for other_enum_member in self.enum_parent.adapted_enum_decls:
            other_enum_value_cpp_name = other_enum_member.cpp_element().name_code()
            assert other_enum_value_cpp_name is not None
            other_enum_value_python_name = cpp_to_python.enum_value_name_to_python(
                self.options, self.enum_parent.cpp_element(), other_enum_member.cpp_element()
            )
            enum_name = self.enum_parent.enum_name_python()

            replacement = code_replacements.StringReplacement()
            replacement.replace_what = r"\b" + other_enum_value_cpp_name + r"\b"
            replacement.by_what = f"Literal[{enum_name}.{other_enum_value_python_name}]"
            decl_value_python = code_replacements.apply_one_replacement(decl_value_python, replacement)

        return decl_value_python

    # override
    def _str_stub_lines(self) -> List[str]:
        lines = []
        decl_name = self.decl_name_python()
        decl_value = self.decl_value_python()
        decl_part = f"{decl_name} = {decl_value}"

        cpp_decl = self.cpp_element()
        if self.comment_python_shall_place_at_end_of_line():
            decl_line = decl_part + cpp_to_python.comment_python_end_of_line(self.options, cpp_decl)
            lines.append(decl_line)
        else:
            comment_lines = cpp_to_python.comment_python_previous_lines(self.options, cpp_decl)
            lines += comment_lines
            lines.append(decl_part)

        return self._cpp_original_code_lines() + lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        decl_name_cpp = self.decl_name_cpp_decorated()
        decl_name_python = self.decl_name_python()
        value_comment = self.comment_pydef_one_line()
        line = f'.value("{decl_name_python}", {decl_name_cpp}, "{value_comment}")'
        return [line]


@dataclass
class AdaptedEnum(AdaptedElement):
    adapted_children: List[Union[AdaptedDecl, AdaptedEmptyLine, AdaptedComment]]
    adapted_enum_decls: List[AdaptedEnumDecl]

    def __init__(self, options: LitgenOptions, enum_: CppEnum) -> None:
        super().__init__(options, enum_)
        self.adapted_children = []
        self.adapted_enum_decls = []
        self._fill_children()

    # override
    def cpp_element(self) -> CppEnum:
        return cast(CppEnum, self._cpp_element)

    def enum_name_python(self) -> str:
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().enum_name)
        return r

    def _fill_children(self) -> None:
        children_with_values = self.cpp_element().get_children_with_filled_decl_values(self.options.srcml_options)
        for c_child in children_with_values:
            if isinstance(c_child, CppEmptyLine):
                self.adapted_children.append(AdaptedEmptyLine(self.options, c_child))
            elif isinstance(c_child, CppComment):
                self.adapted_children.append(AdaptedComment(self.options, c_child))
            elif isinstance(c_child, CppDecl):
                is_count = cpp_to_python.enum_element_is_count(self.options, self.cpp_element(), c_child)
                if not is_count:
                    new_adapted_decl = AdaptedEnumDecl(self.options, c_child, self)
                    self.adapted_children.append(new_adapted_decl)
                    self.adapted_enum_decls.append(new_adapted_decl)

    def get_adapted_decls(self) -> List[AdaptedDecl]:
        decls = list(filter(lambda c: isinstance(c, AdaptedDecl), self.adapted_children))
        return cast(List[AdaptedDecl], decls)

    # override
    def _str_stub_lines(self) -> List[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerPython

        line_spacer = LineSpacerPython(self.options)

        title_line = f"class {self.cpp_element().enum_name}(Enum):"

        body_lines: List[str] = []
        for child in self.adapted_children:
            element_lines = child._str_stub_lines()
            spacing_lines = line_spacer.spacing_lines(child, element_lines)
            body_lines += spacing_lines
            body_lines += element_lines

        all_lines = self._str_stub_layout_lines([title_line], body_lines)
        return all_lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        enum_name_cpp = self.cpp_element().enum_name
        enum_name_python = self.enum_name_python()
        comment = self.comment_pydef_one_line()
        location = self.info_original_location_cpp()

        lines: List[str] = []

        # Enum decl first line
        enum_decl_line = f'py::enum_<{enum_name_cpp}>(m, "{enum_name_python}", py::arithmetic(), "{comment}"){location}'
        lines += [enum_decl_line]

        # Enum values
        for child in self.adapted_children:
            if isinstance(child, AdaptedEnumDecl):
                adapted_decl = cast(AdaptedEnumDecl, child)
                value_decl_lines = adapted_decl._str_pydef_lines()
                lines += value_decl_lines

        # Add ; on the last line
        assert len(lines) > 0
        last_line = lines[-1]
        last_line = code_utils.add_item_before_cpp_comment(last_line, ";")
        lines[-1] = last_line

        # indent lines
        lines = code_utils.indent_code_lines(lines, skip_first_line=True, indent_str=self.options.indent_cpp_spaces())

        return lines

    def __str__(self) -> str:
        return self.str_stub()
