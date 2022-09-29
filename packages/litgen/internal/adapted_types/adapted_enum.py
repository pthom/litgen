from __future__ import annotations
from typing import Union, cast

from codemanip.code_replacements import RegexReplacementList, RegexReplacement

from srcmlcpp.srcml_types import *

from litgen.internal import cpp_to_python
from litgen.internal.context.litgen_context import LitgenContext
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_decl import AdaptedDecl
from litgen.internal.adapted_types.adapted_element import AdaptedElement


@dataclass
class AdaptedEnumDecl(AdaptedDecl):
    enum_parent: AdaptedEnum

    def __init__(self, lg_context: LitgenContext, decl: CppDecl, enum_parent: AdaptedEnum) -> None:
        self.enum_parent = enum_parent
        super().__init__(lg_context, decl)

    # override
    def cpp_element(self) -> CppDecl:
        return cast(CppDecl, self._cpp_element)

    def decl_name_cpp_decorated(self) -> str:
        is_class_enum = self.enum_parent.cpp_element().enum_type == "class"

        scope_str = self.enum_parent.cpp_element().cpp_scope(is_class_enum).str_cpp()
        decl_name_cpp = self.cpp_element().decl_name

        if len(scope_str) > 0:
            r = scope_str + "::" + decl_name_cpp
        else:
            r = decl_name_cpp
        return r

    def _decl_name_cpp_without_enum_prefix(self) -> str:
        enum_cpp = self.enum_parent.cpp_element()
        enum_element_cpp = self.cpp_element()
        value_name_cpp = enum_element_cpp.decl_name

        if not self.options.enum_flag_remove_values_prefix or enum_cpp.enum_type == "class":
            return value_name_cpp

        enum_name_cpp = enum_cpp.enum_name
        decl_name_cpp_no_prefix = value_name_cpp
        if value_name_cpp.upper().startswith(enum_name_cpp.upper() + "_"):
            decl_name_cpp_no_prefix = value_name_cpp[len(enum_name_cpp) + 1 :]
        elif value_name_cpp.upper().startswith(enum_name_cpp.upper()):
            decl_name_cpp_no_prefix = value_name_cpp[len(enum_name_cpp) :]

        if len(decl_name_cpp_no_prefix) == 0:
            decl_name_cpp_no_prefix = value_name_cpp
        if decl_name_cpp_no_prefix[0].isdigit():
            decl_name_cpp_no_prefix = "_" + decl_name_cpp_no_prefix

        return decl_name_cpp_no_prefix

    def decl_name_python(self) -> str:
        decl_name_cpp_without_enum_prefix = self._decl_name_cpp_without_enum_prefix()
        r = cpp_to_python.var_name_to_python(self.options, decl_name_cpp_without_enum_prefix)
        return r

    def decl_value_python(self) -> str:
        decl_value_cpp = self.cpp_element().initial_value_code
        decl_value_python = cpp_to_python.var_value_to_python(self.lg_context, decl_value_cpp)

        # Sometimes, enum decls have interdependent values like this:
        #     enum MyEnum { /*....*/ MyEnum_foo = MyEnum_a | MyEnum_b };
        # So, we search and replace enum strings in the default value
        replacements = self.enum_parent.cpp_to_python_replacements(from_inside_block=True)
        decl_value_python = replacements.apply(decl_value_python)

        return decl_value_python

    def cpp_to_python_replacements(self, from_inside_block: bool = False) -> RegexReplacementList:
        replacement_list = RegexReplacementList()

        enum_name_cpp = self.enum_parent.cpp_element().enum_name
        enum_member_name_cpp = self.cpp_element().decl_name
        enum_name_python = enum_name_cpp
        enum_member_name_python = self.decl_name_python()

        is_enum_class = self.enum_parent.cpp_element().is_enum_class()

        by_what = f"{enum_name_python}.{enum_member_name_python}"
        if is_enum_class:
            replace_what = rf"\b{enum_name_cpp}.{enum_member_name_cpp}\b|{enum_name_cpp}.{enum_member_name_cpp}\b"
            replacement = RegexReplacement(replace_what, by_what)
            replacement_list.add_replacement(replacement)
        else:
            if enum_member_name_cpp.lower().startswith(enum_name_cpp.lower()):
                replace_what = rf"\b{enum_member_name_cpp}\b"
                replacement = RegexReplacement(replace_what, by_what)
                replacement_list.add_replacement(replacement)
            else:
                # No replacement, this could lead to many unwanted replacements!
                # Only accept this if we are inside the enum generation
                if from_inside_block:
                    replace_what_inside = rf"\b{enum_member_name_cpp}\b"
                    replacement_inside_block = RegexReplacement(replace_what_inside, by_what)
                    replacement_list.add_replacement(replacement_inside_block)

        return replacement_list

    # override
    def _str_stub_lines(self) -> List[str]:
        lines = []
        decl_name = self.decl_name_python()
        decl_value = self.decl_value_python()
        decl_part = f"{decl_name} = auto() # (= {decl_value})"

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

    def __str__(self):
        return str(self.cpp_element())


@dataclass
class AdaptedEnum(AdaptedElement):
    adapted_children: List[Union[AdaptedDecl, AdaptedEmptyLine, AdaptedComment]]
    adapted_enum_decls: List[AdaptedEnumDecl]

    def __init__(self, lg_context: LitgenContext, enum_: CppEnum) -> None:
        super().__init__(lg_context, enum_)
        self.adapted_children = []
        self.adapted_enum_decls = []
        self._fill_children()

        replacements = self.cpp_to_python_replacements()
        self.lg_context.replacements_cache.store_replacements(replacements)

    # override
    def cpp_element(self) -> CppEnum:
        return cast(CppEnum, self._cpp_element)

    def enum_name_python(self) -> str:
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().enum_name)
        return r

    def _fill_children(self) -> None:
        children_with_values = self.cpp_element().get_children_with_filled_decl_values()
        for c_child in children_with_values:
            if isinstance(c_child, CppEmptyLine):
                self.adapted_children.append(AdaptedEmptyLine(self.lg_context, c_child))
            elif isinstance(c_child, CppComment):
                self.adapted_children.append(AdaptedComment(self.lg_context, c_child))
            elif isinstance(c_child, CppDecl):
                is_count = cpp_to_python.enum_element_is_count(self.options, self.cpp_element(), c_child)
                if not is_count:
                    new_adapted_decl = AdaptedEnumDecl(self.lg_context, c_child, self)
                    self.adapted_children.append(new_adapted_decl)
                    self.adapted_enum_decls.append(new_adapted_decl)

    def cpp_to_python_replacements(self, from_inside_block: bool = False) -> RegexReplacementList:
        r = RegexReplacementList()
        for decl in self.adapted_enum_decls:
            r.merge_replacements(decl.cpp_to_python_replacements(from_inside_block))
        return r

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
        enum_name_cpp = self.cpp_element().cpp_scope(True).str_cpp()
        # enum_name_cpp = self.cpp_element().enum_name
        enum_name_python = self.enum_name_python()
        comment = self.comment_pydef_one_line()
        location = self.info_original_location_cpp()

        lines: List[str] = []

        # Enum decl first line
        is_arithmetic = code_utils.does_match_regex(self.options.enum_make_arithmetic__regex, enum_name_cpp)
        arithmetic_str = ", py::arithmetic()" if is_arithmetic else ""
        pydef_class_var_parent = cpp_to_python.cpp_scope_to_pybind_parent_var_name(self.options, self.cpp_element())
        enum_decl_line = f'py::enum_<{enum_name_cpp}>({pydef_class_var_parent}, "{enum_name_python}"{arithmetic_str}, "{comment}"){location}'
        lines += [enum_decl_line]

        # Enum values
        for child in self.adapted_children:
            if isinstance(child, AdaptedEnumDecl):
                adapted_decl = child
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
