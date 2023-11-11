from __future__ import annotations

from codemanip import code_utils

from srcmlcpp.cpp_types.base.cpp_access_type import CppAccessType
from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppPublicProtectedPrivate"]


class CppPublicProtectedPrivate(CppBlock):  # Also a CppElementAndComment
    """A kind of block defined by a public/protected/private zone in a struct or in a class

    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types, and we derive from CppBlockContent
    """

    access_type: CppAccessType = CppAccessType.public  # "public", "private", or "protected"
    default_or_explicit: str = ""  # "default" or "" ("default" means it was added automatically)

    def __init__(self, element: SrcmlWrapper, access_type: CppAccessType, default_or_explicit: str | None) -> None:
        super().__init__(element)
        assert default_or_explicit in [None, "", "default"]
        self.access_type = access_type
        self.default_or_explicit = default_or_explicit if default_or_explicit is not None else ""

    def str_public_protected_private(self) -> str:
        r = ""

        if len(self.cpp_element_comments.comment_on_previous_lines) > 0:
            r += self.cpp_element_comments.comment_on_previous_lines
        r += f"{self.access_type.name}" + ":"
        if self.default_or_explicit == "default":
            r += " // <default_access_type/>"
        elif len(self.cpp_element_comments.comment_end_of_line) > 0:
            r += self.cpp_element_comments.comment_end_of_line
        r += "\n"

        r += code_utils.indent_code(self.str_block(), indent_str=self.options.indent_cpp_str)
        return r

    def str_code(self) -> str:
        return self.str_public_protected_private()

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False) -> str:  # noqa
        return self.str_code()

    def __str__(self) -> str:
        return self.str_public_protected_private()
