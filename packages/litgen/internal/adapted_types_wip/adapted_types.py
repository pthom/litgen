from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import cast, List, Union

from srcmlcpp.srcml_types import *

from litgen import LitgenOptions
from litgen.internal.adapt_function import AdaptedFunction
from litgen.internal import cpp_to_python


@dataclass
class AdaptedElement(ABC):
    _cpp_element: CppElementAndComment
    options: LitgenOptions

    def __init__(self, cpp_element: CppElementAndComment, options: LitgenOptions):
        self._cpp_element = cpp_element
        self.options = options

    def cpp_element(self):
        # please implement cpp_element in derived classes
        assert False


@dataclass
class AdaptedEmptyLine(AdaptedElement):
    def __init__(self, cpp_empty_line: CppEmptyLine, options: LitgenOptions):
        super().__init__(cpp_empty_line, options)

    def cpp_element(self) -> CppEmptyLine:
        return cast(CppEmptyLine, self._cpp_element)


@dataclass
class AdaptedDecl(AdaptedElement):
    def __init__(self, decl: CppDecl, options: LitgenOptions):
        super().__init__(decl, options)

    def cpp_element(self):
        return cast(CppDecl, self._cpp_element)


# @dataclass
# class AdaptedEnumDecl(AdaptedDecl):
#
#     # C/C++  Enums members do not always state their value
#     enum_value: str
#
#     def __init__(self, decl: CppDecl, previous_decl: Optional[AdaptedEnumDecl], options: LitgenOptions):
#         super().__init__(decl, options)
#         self._fill_value(previous_decl)
#
#     def cpp_element(self):
#         return cast(CppDecl, self._cpp_element)
#
#     def _fill_value(self, previous_decl: Optional[AdaptedEnumDecl]):
#         # This belongs to CppEnum !!!
#         cpp_value_code = self.cpp_element().initial_value_code
#         if len(cpp_value_code) > 0:
#             self.enum_value = cpp_value_code
#         elif previous_decl is None:
#             # The first enum member value is 0 by default in C/C++
#             self.enum_value = "0"
#         else:
#             assert len(previous_decl.enum_value) > 0


@dataclass
class AdaptedComment(AdaptedElement):
    def __init(self, cpp_comment: CppComment, options: LitgenOptions):
        super().__init__(cpp_comment, options)

    def cpp_element(self):
        return cast(CppComment, self._cpp_element)


@dataclass
class AdaptedConstructor(AdaptedElement):
    def __init__(self, ctor: CppConstructorDecl, options: LitgenOptions):
        super().__init__(ctor, options)

    def cpp_element(self):
        return cast(CppConstructorDecl, self._cpp_element)


@dataclass
class AdaptedClass(AdaptedElement):
    def __init__(self, class_: CppStruct, options: LitgenOptions):
        super().__init__(class_, options)

    def cpp_element(self) -> CppStruct:
        return cast(CppStruct, self._cpp_element)

    def class_name_python(self):
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().class_name)
        return r


@dataclass
class AdaptedEnum(AdaptedElement):
    children: List[Union[AdaptedDecl, AdaptedEmptyLine, AdaptedComment]]

    def __init__(self, enum_: CppEnum, options: LitgenOptions):
        super().__init__(enum_, options)
        self.children = []
        self._fill_children()

    def cpp_element(self):
        return cast(CppEnum, self._cpp_element)

    def enum_name_python(self):
        r = cpp_to_python.add_underscore_if_python_reserved_word(self.cpp_element().enum_name)
        return r

    def _fill_children(self):
        children_with_values = self.cpp_element().get_children_with_filled_decl_values(self.options.srcml_options)
        for c_child in children_with_values:
            if isinstance(c_child, CppEmptyLine):
                self.children.append(AdaptedEmptyLine(c_child, self.options))
            elif isinstance(c_child, CppComment):
                self.children.append(AdaptedComment(c_child, self.options))
            elif isinstance(c_child, CppDecl):
                new_adapted_decl = AdaptedDecl(c_child, self.options)
                is_count = cpp_to_python.enum_element_is_count(
                    self.cpp_element(), new_adapted_decl.cpp_element(), self.options
                )
                if not is_count:
                    self.children.append(new_adapted_decl)

    def get_decls(self) -> List[AdaptedDecl]:
        decls = list(filter(lambda c: isinstance(c, AdaptedDecl), self.children))
        return cast(List[AdaptedDecl], decls)


@dataclass
class AdaptedCppUnit(AdaptedElement):
    def __init__(self, cpp_unit: CppUnit, options: LitgenOptions):
        super().__init__(cpp_unit, options)

    def cpp_element(self):
        return cast(CppUnit, self._cpp_element)
