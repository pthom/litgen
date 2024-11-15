from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Callable

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.scrml_warning_settings import WarningType
from srcmlcpp.cpp_types.decls_types.cpp_decl import CppDecl
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppParameter"]


# Array of precompiled patterns for immutables
_IMMUTABLE_VALUES_PATTERNS = [
    # Floating point literals with optional suffixes (e.g., 1.5f, 2.0, .5L)
    re.compile(
        r"""
        ^                       # Start of string
        -?                      # Optional negative sign
        (?:                     # Non-capturing group for the number
            \d+\.\d*            # Digits followed by a dot and optional digits (e.g., 1.5)
            |\.\d+              # Dot followed by digits (e.g., .5)
            |\d+                # Digits only (e.g., 2)
        )
        (?:[eE][+-]?\d+)?       # Optional exponent part (e.g., e10, e-5)
        [fFdDlL]?               # Optional floating-point suffix
        $                       # End of string
        """,
        re.VERBOSE,
    ),
    # Integer literals with optional suffixes (e.g., 42u, 0x1AUL, -100LL)
    re.compile(
        r"""
        ^                       # Start of string
        -?                      # Optional negative sign
        (?:
            0[xX][\da-fA-F]+    # Hexadecimal integer (e.g., 0x1A)
            |0[bB][01]+         # Binary integer (e.g., 0b1010)
            |0[oO][0-7]+        # Octal integer (e.g., 0o755)
            |[1-9]\d*           # Decimal integer (e.g., 42)
            |0                  # Zero (e.g., 0)
        )
        [uUlL]*                 # Optional integer suffixes
        $                       # End of string
        """,
        re.VERBOSE,
    ),
    re.compile(r'^".*"$'),  # String literal (e.g., "hello")
    re.compile(r"^'.{1,2}'$"),  # Character literal (e.g., 'a', '\n')
]
# Immutable keywords that don't require regex matching
_IMMUTABLE_VALUES_KEYWORDS = ["nullptr", "NULL", "true", "false", "TRUE", "FALSE", "nullopt", "std::nullopt"]


_BASE_IMMUTABLE_TYPES = [
    # Base integer types
    "int",
    "signed int",
    "unsigned int",
    "char",
    "signed char",
    "unsigned char",
    "long",
    "signed long",
    "unsigned long",
    "long long",
    "signed long long",
    "unsigned long long",
    "short",
    "signed short",
    "unsigned short",

    # Base floating point types
    "float",
    "double",
    "long double",
    "float32_t",
    "float64_t",
    "float128_t",

    # Boolean type
    "bool",

    # String types
    "std::string",
    "std::string_view",
    "std::wstring",
    "std::u16string",
    "std::u32string",

    # Byte type
    "std::byte",

    # Fixed-width integer types
    "int8_t",
    "int16_t",
    "int32_t",
    "int64_t",
    "uint8_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "intptr_t",
    "uintptr_t",

    # Size types
    "size_t",
    "ssize_t",
    "std::size_t",
]


def _looks_like_mutable_default_value(
        initial_value_code: str,
        fn_is_known_immutable_type: Callable[[str], bool] | None,
        fn_is_known_immutable_value: Callable[[str], bool] | None,
) -> bool:
    """Return True if the initial_value_code looks like a mutable default value.
    initial_value_code is the code that is used to initialize the parameter, e.g.
        int x = 5;  => initial_value_code = "5"

    additional_immutable_types__regex is a regex pattern that matches additional types that are considered immutable.
    They might be separated by a pipe character, e.g. exclude all type endings with "Int|UInt":
        additional_immutable_types__regex = r"Int|UInt"

    This is only a heuristic, but it is enough for our needs:
    We will return False if the code is certainly immutable, and True otherwise.
    The following cases are considered as immutable:
        - float, int, double, etc.
        - string literals
        - nullptr or NULL
    """
    initial_value_code = initial_value_code.strip()

    # Test the value
    if True:  # just to have a block
        if fn_is_known_immutable_value is not None and fn_is_known_immutable_value(initial_value_code):
                return False

        for pattern in _IMMUTABLE_VALUES_PATTERNS:
            if pattern.match(initial_value_code):
                return False

        if initial_value_code in _IMMUTABLE_VALUES_KEYWORDS:
            return False

    # Test the value type if available
    if True: # just to have a block
        def try_extract_type() -> str | None:
            r = None
            if "(" in initial_value_code:
                r = initial_value_code.split("(")[0]
            if "{" in initial_value_code:
                r = initial_value_code.split("{")[0]
            return r

        initial_value_type = try_extract_type()
        if initial_value_type is not None:
            if initial_value_type in _BASE_IMMUTABLE_TYPES:
                return False
            if fn_is_known_immutable_type is not None and fn_is_known_immutable_type(initial_value_type):
                    return False

    # Default to True for values that look mutable or ambiguous
    return True


@dataclass
class CppParameter(CppElementAndComment):
    """
    Most of the time CppParameter is a function parameter.
    However, template parameter are also concerned
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    _decl: CppDecl

    template_type: str  # This is only for template's CppParameterList (will be "typename" or "class")
    template_name: str = ""  # This is only for template's CppParameterList (name of the template type, e.g. "T")
    template_init: str = ""  # For templates with default int value, e.g. `template<int N=1> void f()`

    def __init__(self, element: SrcmlWrapper) -> None:
        dummy_cpp_element_comments = CppElementComments()
        super().__init__(element, dummy_cpp_element_comments)

    @property
    def decl(self) -> CppDecl:
        return self._decl

    @decl.setter
    def decl(self, new_decl: CppDecl) -> None:
        self._decl = new_decl
        self._decl.parent = self

    def type_name_default_for_signature(self) -> str:
        assert hasattr(self, "decl")
        r = self.decl.type_name_default_for_signature()
        return r

    def str_code(self) -> str:
        if hasattr(self, "decl"):
            assert not hasattr(self, "template_type")
            return str(self.decl)
        else:
            if not hasattr(self, "template_type"):
                self.emit_warning("CppParameter.__str__() with no decl and no template_type", WarningType.Unclassified)
            return str(self.template_type) + " " + self.template_name

    def str_template_type(self) -> str:
        assert hasattr(self, "template_type")
        r = str(self.template_type) + " " + self.template_name
        return r

    def is_template_param(self) -> bool:
        r = hasattr(self, "template_type")
        return r

    def seems_mutable_param_with_default_value(
            self,
            fn_is_immutable_type: Callable[[str], bool] | None = None,
            fn_is_immutable_value: Callable[[str], bool] | None = None,
    ) -> bool:
        """Determines whether the parameter with a default value appears to be mutable."""

        decl = self.decl
        cpp_type = decl.cpp_type

        # Bail out if the parameter has no default value
        initial_value_code = decl.initial_value_code.strip()
        if len(initial_value_code) == 0:
            return False

        # Check for types we cannot handle or that suggest mutability
        if "&&" in cpp_type.modifiers:
            return False  # R-value references are not supported
        if cpp_type.is_raw_pointer():
            return False  # Pointers may refer to mutable data
        if "..." in cpp_type.modifiers:
            return False  # Variadic arguments are not considered
        if cpp_type.is_void():
            return False  # Void type does not hold value

        # Determine if the parameter is a const reference or a value type
        is_const_ref = cpp_type.is_reference() and cpp_type.is_const()
        is_value_type = not cpp_type.is_reference()

        # If it's a non-const reference, we should not accept mutable defaults
        if not (is_const_ref or is_value_type):
            return False

        # Check if the default value looks like a mutable object
        if True:  # just to have a block
            decl_type_str = cpp_type.str_code()
            if decl_type_str in _BASE_IMMUTABLE_TYPES:
                return False
            if fn_is_immutable_type is not None and fn_is_immutable_type(decl_type_str):
                return False

        # Check if the default value looks like a mutable object
        r = _looks_like_mutable_default_value(initial_value_code, fn_is_immutable_type, fn_is_immutable_value)
        return r

    def __str__(self) -> str:
        return self.str_code()

    def __repr__(self):
        return self.str_code()

    def full_type(self) -> str:
        r = self.decl.cpp_type.str_code()
        return r

    def has_default_value(self) -> bool:
        return len(self.decl.initial_value_code) > 0

    def default_value(self) -> str:
        return self.decl.initial_value_code

    def variable_name(self) -> str:
        return self.decl.decl_name

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)

        cpp_visitor_function(self, CppElementsVisitorEvent.OnBeforeChildren, depth)
        if hasattr(self, "decl"):
            self.decl.visit_cpp_breadth_first(cpp_visitor_function, depth + 1)
        cpp_visitor_function(self, CppElementsVisitorEvent.OnAfterChildren, depth)
