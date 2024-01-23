from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import CppElementComments
from srcmlcpp.cpp_types.functions.cpp_function_decl import CppFunctionDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppConstructorDecl"]


@dataclass
class CppConstructorDecl(CppFunctionDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)
        self.specifiers: list[str] = []
        self.function_name = ""

    def _str_signature(self) -> str:
        r = f"{self.function_name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
        return r

    def str_full_return_type(self) -> str:
        return ""

    def str_code(self) -> str:
        return self._str_signature()

    def __str__(self) -> str:
        return self.str_commented()

    def __repr__(self):
        return self._str_signature()
