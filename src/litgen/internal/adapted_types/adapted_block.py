from __future__ import annotations
from dataclasses import dataclass
from typing import Union, cast

from codemanip import code_utils
from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp.cpp_types import (
    CppBlock,
    CppComment,
    CppConditionMacro,
    CppDeclStatement,
    CppDefine,
    CppEmptyLine,
    CppEnum,
    CppFunctionDecl,
    CppNamespace,
    CppStruct,
)
from srcmlcpp.srcmlcpp_exception import SrcmlcppException
from srcmlcpp.scrml_warning_settings import WarningType

from litgen.internal.adapted_types.adapted_class import AdaptedClass
from litgen.internal.adapted_types.adapted_comment import (
    AdaptedComment,
    AdaptedEmptyLine,
)
from litgen.internal.adapted_types.adapted_element import (
    _PROGRESS_BAR_TITLE_PYDEF,
    _PROGRESS_BAR_TITLE_STUB,
    AdaptedElement,
)
from litgen.internal.adapted_types.adapted_enum import AdaptedEnum
from litgen.internal.adapted_types.adapted_function import AdaptedFunction
from litgen.internal.context.litgen_context import LitgenContext
from litgen.internal.adapted_types.adapted_define import AdaptedDefine
from litgen.internal.adapted_types.adapted_condition_macro import AdaptedConditionMacro
from litgen.internal.adapted_types.adapted_decl import AdaptedGlobalDecl


@dataclass
class AdaptedBlock(AdaptedElement):
    adapted_elements: list[
        Union[
            AdaptedEmptyLine,
            # AdaptedDecl,        # Variable declarations are not published in the bindings
            AdaptedComment,
            AdaptedClass,
            AdaptedFunction,
            AdaptedEnum,
            AdaptedDefine,
            AdaptedConditionMacro
            # AdaptedNamespace,  # There is actually a circular dependency here (with no important consequences)
            # A Block can contain a namespace, and a namespace contains a block
        ]
    ]

    def __init__(self, lg_context: LitgenContext, block: CppBlock) -> None:
        super().__init__(lg_context, block)
        self.adapted_elements = []
        self._fill_adapted_elements()

    # override
    def cpp_element(self) -> CppBlock:
        return cast(CppBlock, self._cpp_element)

    def _fill_adapted_elements(self) -> None:
        from litgen.internal.adapted_types.adapted_namespace import AdaptedNamespace

        for child in self.cpp_element().block_children:
            try:
                if isinstance(child, CppEmptyLine):
                    self.adapted_elements.append(AdaptedEmptyLine(self.lg_context, child))
                elif isinstance(child, CppComment):
                    self.adapted_elements.append(AdaptedComment(self.lg_context, child))
                elif isinstance(child, CppConditionMacro):
                    self.adapted_elements.append(AdaptedConditionMacro(self.lg_context, child))
                elif isinstance(child, CppStruct):
                    is_excluded_by_name = code_utils.does_match_regex(
                        self.options.class_exclude_by_name__regex, child.class_name
                    )
                    if not is_excluded_by_name:
                        self.adapted_elements.append(AdaptedClass(self.lg_context, child))
                elif isinstance(child, CppFunctionDecl):
                    if AdaptedFunction.init_is_function_publishable(self.options, child):
                        is_overloaded = self.cpp_element().is_function_overloaded(child)
                        self.adapted_elements.append(AdaptedFunction(self.lg_context, child, is_overloaded))
                elif isinstance(child, CppDefine):
                    is_included = code_utils.does_match_regex(
                        self.options.macro_define_include_by_name__regex, child.macro_name
                    )
                    is_publishable = AdaptedDefine.is_publishable(child)
                    if is_included and is_publishable:
                        self.adapted_elements.append(AdaptedDefine(self.lg_context, child))
                elif isinstance(child, CppEnum):
                    is_excluded_by_name = code_utils.does_match_regex(
                        self.options.enum_exclude_by_name__regex, child.enum_name
                    )
                    if not is_excluded_by_name:
                        self.adapted_elements.append(AdaptedEnum(self.lg_context, child))
                elif isinstance(child, CppNamespace):
                    is_anonymous_namespace = child.ns_name == ""
                    is_excluded_by_name = code_utils.does_match_regex(
                        self.options.namespace_exclude__regex, child.ns_name
                    )
                    has_block = hasattr(child, "_block")
                    if has_block and not is_excluded_by_name and not is_anonymous_namespace:
                        self.adapted_elements.append(AdaptedNamespace(self.lg_context, child))  # type: ignore
                elif isinstance(child, CppDeclStatement):
                    # We should filter by Unit or Namespace, But we don't have the info at the time being.
                    # # isinstance(self, (AdaptedUnit, AdaptedNamespace)):
                    if True:
                        for cpp_decl in child.cpp_decls:
                            # print(f"Add global: class={self.__class__} decl={cpp_decl}")
                            is_included = code_utils.does_match_regex(
                                self.options.globals_vars_include_by_name__regex, cpp_decl.decl_name
                            )
                            if is_included:
                                self.adapted_elements.append(AdaptedGlobalDecl(self.lg_context, cpp_decl))  # type: ignore
            except SrcmlcppException as e:
                child.emit_warning(str(e), WarningType.LitgenBlockElementException)

    # override
    def stub_lines(self) -> list[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element in self.adapted_elements:
            element_lines = adapted_element.stub_lines()

            current_line = adapted_element.cpp_element().start().line
            global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_STUB, current_line)

            if not self.options.python_reproduce_cpp_layout:
                spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
                lines += spacing_lines

            lines += element_lines
        return lines

    # override
    def pydef_lines(self) -> list[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element in self.adapted_elements:
            current_line = adapted_element.cpp_element().start().line
            global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_PYDEF, current_line)

            element_lines = adapted_element.pydef_lines()

            spacing_lines = line_spacer.spacing_lines(adapted_element, element_lines)
            lines += spacing_lines

            lines += element_lines
        return lines
