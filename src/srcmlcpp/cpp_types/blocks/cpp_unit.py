from __future__ import annotations
import re
from dataclasses import dataclass

from srcmlcpp.cpp_types.base.cpp_element import CppElement
from srcmlcpp.cpp_types.blocks.cpp_block import CppBlock
from srcmlcpp.srcml_wrapper import SrcmlWrapper
from srcmlcpp.cpp_types.scope.cpp_scope_identifiers import CppScopeIdentifiers


__all__ = ["CppUnit"]


def _parse_c_int_literal(text: str) -> int | None:
    """Parse a C integer literal (decimal, hex, octal), tolerating surrounding
    whitespace and integer suffixes (u/U/l/L). Returns None if not an int literal."""
    core = text.strip().rstrip("uUlL")
    if len(core) == 0:
        return None
    try:
        if re.fullmatch(r"0[0-7]+", core):  # C-style octal (e.g. 010)
            return int(core, 8)
        return int(core, 0)  # handles decimal, 0x..., 0o..., 0b...
    except ValueError:
        return None


@dataclass
class CppUnit(CppBlock):
    """A kind of block representing a full file."""

    _scope_identifiers: CppScopeIdentifiers
    _int_defines_cache: dict[str, int] | None

    def __init__(self, element: SrcmlWrapper) -> None:
        super().__init__(element)
        self._scope_identifiers = CppScopeIdentifiers()
        self._int_defines_cache = None

    def __str__(self) -> str:
        return self.str_block()

    def str_code(self) -> str:
        return self.str_block()

    def __repr__(self):
        if self.filename is None:
            return "CppUnit"
        else:
            return "CppUnit: " + self.filename

    @staticmethod
    def find_root_cpp_unit(element: CppElement) -> CppUnit:
        assert hasattr(element, "parent")  # parent should have been filled by parse_unit & CppBlock

        current = element
        while True:
            root = current
            if current.parent is None:
                break
            current = current.parent

        assert isinstance(root, CppUnit)
        return root

    def fill_scope_identifiers_cache(self) -> None:
        all_elements = self.all_cpp_elements_recursive()
        self._scope_identifiers.fill_cache(all_elements)

    def int_value_from_define_name(self, name: str) -> int | None:
        """Resolve an object-like `#define` whose value is an integer (possibly
        through one or more layers of indirection to another define or to a
        named_number_macros entry). Returns None if it cannot be resolved to an int."""
        if self._int_defines_cache is None:
            self._fill_int_defines_cache()
        assert self._int_defines_cache is not None
        return self._int_defines_cache.get(name)

    def _fill_int_defines_cache(self) -> None:
        from srcmlcpp.cpp_types.cpp_define import CppDefine

        raw_values: dict[str, str] = {}
        for cpp_define in self.all_cpp_elements_recursive(CppDefine):
            assert isinstance(cpp_define, CppDefine)
            if hasattr(cpp_define, "macro_parameters_str"):
                continue  # function-like macro, not a plain value
            if not hasattr(cpp_define, "macro_value"):
                continue
            raw_values[cpp_define.macro_name] = cpp_define.macro_value

        cache: dict[str, int] = {}
        for name in raw_values:
            value = self._resolve_int_token(name, raw_values, set())
            if value is not None:
                cache[name] = value
        self._int_defines_cache = cache

    def _resolve_int_token(self, token: str, raw_values: dict[str, str], seen: set[str]) -> int | None:
        token = token.strip()
        # Remove possible surrounding parentheses (often used in macros)
        while len(token) >= 2 and token.startswith("(") and token.endswith(")"):
            token = token[1:-1].strip()

        as_literal = _parse_c_int_literal(token)
        if as_literal is not None:
            return as_literal

        # Indirection: the token is another macro name
        if token in self.options.named_number_macros:
            return self.options.named_number_macros[token]
        if token in raw_values and token not in seen:
            seen.add(token)
            return self._resolve_int_token(raw_values[token], raw_values, seen)
        return None
