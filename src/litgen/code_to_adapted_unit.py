from __future__ import annotations
from typing import Optional

import srcmlcpp

from litgen.internal.adapted_types.adapted_unit import (
    AdaptedUnit,
    LitgenContext,
)

from litgen.options import LitgenOptions


def _remove_all_comments(cpp_unit: srcmlcpp.CppUnit) -> None:
    def cpp_visitor_function(
        cpp_element: srcmlcpp.CppElement, event: srcmlcpp.CppElementsVisitorEvent, depth: int
    ) -> None:
        if event == srcmlcpp.CppElementsVisitorEvent.OnElement:
            if isinstance(cpp_element, srcmlcpp.CppElementAndComment):
                cpp_element.cpp_element_comments.comment_end_of_line = ""
                cpp_element.cpp_element_comments.comment_on_previous_lines = ""

    cpp_unit.visit_cpp_breadth_first(cpp_visitor_function)


def code_to_adapted_unit_in_context(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
) -> AdaptedUnit:
    cpp_unit = srcmlcpp.code_to_cpp_unit(lg_context.options.srcmlcpp_options, code, filename)

    if lg_context.options.comments_exclude:
        _remove_all_comments(cpp_unit)

    adapted_unit = AdaptedUnit(lg_context, cpp_unit)

    return adapted_unit


def code_to_adapted_unit(
    options: LitgenOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> AdaptedUnit:
    lg_context = LitgenContext(options)
    return code_to_adapted_unit_in_context(lg_context, code, filename)
