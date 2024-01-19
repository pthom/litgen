from __future__ import annotations
from dataclasses import dataclass
from typing import cast

from srcmlcpp.cpp_types import CppComment, CppEmptyLine

from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.context.litgen_context import LitgenContext


@dataclass
class AdaptedEmptyLine(AdaptedElement):
    def __init__(self, lg_context: LitgenContext, cpp_empty_line: CppEmptyLine) -> None:
        super().__init__(lg_context, cpp_empty_line)

    # override
    def cpp_element(self) -> CppEmptyLine:
        return cast(CppEmptyLine, self._cpp_element)

    # override
    def stub_lines(self) -> list[str]:
        if self.options.python_reproduce_cpp_layout:
            return [""]
        else:
            return []

    # override
    def pydef_lines(self) -> list[str]:
        return []


@dataclass
class AdaptedComment(AdaptedElement):
    def __init__(self, lg_context: LitgenContext, cpp_comment: CppComment):
        super().__init__(lg_context, cpp_comment)

    # override
    def cpp_element(self) -> CppComment:
        return cast(CppComment, self._cpp_element)

    # override
    def stub_lines(self) -> list[str]:
        comment_cpp = self.cpp_element().comment
        comment_python = cpp_to_python._comment_apply_replacements(self.options, comment_cpp)

        def add_hash(s: str) -> str:
            if self.options.python_reproduce_cpp_layout:
                return "#" + s
            else:
                return "# " + s.lstrip()

        comment_python_lines = list(map(add_hash, comment_python.split("\n")))
        return comment_python_lines

    # override
    def pydef_lines(self) -> list[str]:
        return []
