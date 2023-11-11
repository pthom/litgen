from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import cast
from munch import Munch  # type:ignore

from srcmlcpp.cpp_types import CppDefine
from codemanip import code_utils

from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.context.litgen_context import LitgenContext


class _PreprocessorDefineValueType(Enum):
    Int = 1
    Float = 2
    String = 3
    Hex = 4
    Octal = 5
    Other = 6


def _compute_define_value_type(define_value: str) -> _PreprocessorDefineValueType:
    if define_value.startswith('"') and define_value.endswith('"'):
        return _PreprocessorDefineValueType.String

    nb_dots = define_value.count(".")
    if nb_dots > 1:
        return _PreprocessorDefineValueType.Other
    elif nb_dots == 1:  # Try to parse float
        try:
            _ = float(define_value)
            return _PreprocessorDefineValueType.Float
        except ValueError:
            return _PreprocessorDefineValueType.Other
    else:  # nb_dots == 0 => try to parse int
        if define_value.startswith("0x") or define_value.startswith("0X"):
            try:
                _ = int(define_value, 16)
                return _PreprocessorDefineValueType.Hex
            except ValueError:
                return _PreprocessorDefineValueType.Other
        elif define_value.startswith("0") and len(define_value) > 1:
            try:
                _ = int(define_value, 8)
                return _PreprocessorDefineValueType.Octal
            except ValueError:
                return _PreprocessorDefineValueType.Other
        else:
            try:
                _ = int(define_value)
                return _PreprocessorDefineValueType.Int
            except ValueError:
                return _PreprocessorDefineValueType.Other

    return _PreprocessorDefineValueType.Other


@dataclass
class AdaptedDefine(AdaptedElement):
    def __init__(self, lg_context: LitgenContext, cpp_define: CppDefine):
        super().__init__(lg_context, cpp_define)

    @staticmethod
    def is_publishable(cpp_define: CppDefine) -> bool:
        if hasattr(cpp_define, "macro_parameters_str"):
            return False
        if not hasattr(cpp_define, "macro_value"):
            return False

        if _compute_define_value_type(cpp_define.macro_value) == _PreprocessorDefineValueType.Other:
            return False
        else:
            return True

    def published_name(self) -> str:
        r = self.options.macro_name_replacements.apply(self.cpp_element().macro_name)
        return r

    def published_python_value(self) -> str:
        macro_value = self.cpp_element().macro_value
        if _compute_define_value_type(macro_value) == _PreprocessorDefineValueType.Octal:
            return (
                "0o" + macro_value[1:]
            )  # Python 3.11 require 0o as a prefix for octal values (a good decision indeed)
        else:
            return macro_value

    # override
    def cpp_element(self) -> CppDefine:
        return cast(CppDefine, self._cpp_element)

    # override
    def stub_lines(self) -> list[str]:
        code_template = """{published_name} = {macro_value}"""
        replacements = Munch()
        replacements.published_name = self.published_name()
        replacements.macro_value = self.published_python_value()

        code = code_utils.process_code_template(code_template, replacements)
        comment_lines = cpp_to_python.comment_python_previous_lines(self.options, self.cpp_element())
        r = comment_lines + [code]
        return r

    # override
    def pydef_lines(self) -> list[str]:
        assert AdaptedDefine.is_publishable(self.cpp_element())  # should have been checked by AdaptedBlock
        parent_cpp_module_var_name = cpp_to_python.cpp_scope_to_pybind_var_name(self.options, self.cpp_element())

        code_template = """{m}.attr("{published_name}") = {macro_value};"""

        replacements = Munch()
        replacements.m = parent_cpp_module_var_name
        replacements.published_name = self.published_name()
        replacements.macro_value = self.cpp_element().macro_value

        code = code_utils.process_code_template(code_template, replacements)

        return [code]
