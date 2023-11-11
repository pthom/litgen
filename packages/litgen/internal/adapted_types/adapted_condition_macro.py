from __future__ import annotations
from dataclasses import dataclass
from typing import cast

from srcmlcpp.cpp_types import CppConditionMacro

from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.context.litgen_context import LitgenContext


@dataclass
class AdaptedConditionMacro(AdaptedElement):
    def __init__(self, lg_context: LitgenContext, cpp_condition_macro: CppConditionMacro) -> None:
        super().__init__(lg_context, cpp_condition_macro)

    # override
    def cpp_element(self) -> CppConditionMacro:
        return cast(CppConditionMacro, self._cpp_element)

    # override
    def stub_lines(self) -> list[str]:
        lines = []
        lines += self._elm_comment_python_previous_lines()

        eol_comment = self.cpp_element().cpp_element_comments.eol_comment_code()
        macro_with_eol_comment = self.cpp_element().macro_code + eol_comment

        macro_lines = macro_with_eol_comment.split("\n")
        macro_commented_lines = list(map(lambda s: "# " + s, macro_lines))
        lines += macro_commented_lines

        return lines

    # override
    def pydef_lines(self) -> list[str]:
        lines = self.cpp_element().macro_code.split("\n")
        commented_lines = list(map(lambda s: "// " + s, lines))
        return commented_lines
