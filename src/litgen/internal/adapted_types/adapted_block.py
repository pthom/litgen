from __future__ import annotations
from dataclasses import dataclass
from typing import Union, cast, List

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
        self._group_overloaded_functions()

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
                    is_excluded_by_name = code_utils.does_match_regex_or_matcher(
                        self.options.class_exclude_by_name__regex, child.class_name
                    )
                    if not is_excluded_by_name:
                        self.adapted_elements.append(AdaptedClass(self.lg_context, child))
                elif isinstance(child, CppFunctionDecl):
                    if AdaptedFunction.init_is_function_publishable(self.options, child):
                        is_overloaded = self.cpp_element().is_function_overloaded(child)
                        self.adapted_elements.append(AdaptedFunction(self.lg_context, child, is_overloaded))
                elif isinstance(child, CppDefine):
                    is_included = code_utils.does_match_regex_or_matcher(
                        self.options.macro_define_include_by_name__regex, child.macro_name
                    )
                    is_publishable = AdaptedDefine.is_publishable(child)
                    if is_included and is_publishable:
                        self.adapted_elements.append(AdaptedDefine(self.lg_context, child))
                elif isinstance(child, CppEnum):
                    is_excluded_by_name = code_utils.does_match_regex_or_matcher(
                        self.options.enum_exclude_by_name__regex, child.enum_name
                    )
                    if not is_excluded_by_name:
                        self.adapted_elements.append(AdaptedEnum(self.lg_context, child))
                elif isinstance(child, CppNamespace):
                    is_anonymous_namespace = child.ns_name == ""
                    is_excluded_by_name = code_utils.does_match_regex_or_matcher(
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
                            is_included = code_utils.does_match_regex_or_matcher(
                                self.options.globals_vars_include_by_name__regex, cpp_decl.decl_name
                            )
                            if is_included:
                                self.adapted_elements.append(AdaptedGlobalDecl(self.lg_context, cpp_decl))  # type: ignore
            except SrcmlcppException as e:
                child.emit_warning(str(e), WarningType.LitgenBlockElementException)

    def _group_overloaded_functions(self) -> None:
        """Reorder adapted_elements so that overloaded functions (same name) are adjacent.

        mypy requires @overload-decorated functions to be adjacent in .pyi stubs.
        litgen emits functions in C++ source order, which may interleave overloads
        (e.g. SetWindowSize(size), SetWindowCollapsed(...), SetWindowSize(name, size)).

        This method moves later overloads next to the first occurrence of each name,
        preserving relative order for everything else.
        """
        elements = self.adapted_elements
        # Track the index of the first occurrence of each function name
        fn_first_index: dict[str, int] = {}
        reordered_adapted_elements: List[AdaptedElement] = []
        # Collect elements that need to be inserted after a prior overload
        deferred: dict[str, List[AdaptedElement]] = {}  # function_name -> list of elements to insert

        for elem in elements:
            if isinstance(elem, AdaptedFunction) and elem.is_overloaded:
                name = elem.cpp_element().function_name
                if name not in fn_first_index:
                    # First occurrence: record position and add normally
                    fn_first_index[name] = len(reordered_adapted_elements)
                    reordered_adapted_elements.append(elem)
                else:
                    # Later occurrence: defer it for grouping
                    if name not in deferred:
                        deferred[name] = []
                    deferred[name].append(elem)
            else:
                reordered_adapted_elements.append(elem)

        if not deferred:
            return  # Nothing to reorder

        # Insert deferred overloads right after the first occurrence of each name.
        # Process in reverse order of insertion point so indices stay valid.
        insertions = []
        for name, elems in deferred.items():
            insert_after = fn_first_index[name]
            insertions.append((insert_after, elems))
        insertions.sort(key=lambda x: x[0], reverse=True)

        for insert_after, elems in insertions:
            for j, elem in enumerate(elems):  # type: ignore
                reordered_adapted_elements.insert(insert_after + 1 + j, elem)

        self.adapted_elements = reordered_adapted_elements  # type: ignore

    # override
    def stub_lines(self) -> list[str]:
        from litgen.internal.adapted_types.line_spacer import LineSpacerCpp
        from litgen.internal.adapted_types.stub_overload_dedup import dedup_stub_lines

        line_spacer = LineSpacerCpp()

        lines = []
        for adapted_element, element_lines in dedup_stub_lines(self.adapted_elements):
            current_line = adapted_element.cpp_element().start().line
            global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_STUB, current_line)

            if not self.options.python_reproduce_cpp_layout:
                lines += line_spacer.spacing_lines(adapted_element, element_lines)

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
