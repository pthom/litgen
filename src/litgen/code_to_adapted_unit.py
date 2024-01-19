from __future__ import annotations
from typing import Optional

import srcmlcpp

from litgen.internal.adapted_types.adapted_unit import (
    AdaptedUnit,
    LitgenContext,
)

from litgen.options import LitgenOptions


def code_to_adapted_unit_in_context(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
) -> AdaptedUnit:
    cpp_unit = srcmlcpp.code_to_cpp_unit(lg_context.options.srcmlcpp_options, code, filename)

    adapted_unit = AdaptedUnit(lg_context, cpp_unit)

    return adapted_unit


def code_to_adapted_unit(
    options: LitgenOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> AdaptedUnit:
    lg_context = LitgenContext(options)
    return code_to_adapted_unit_in_context(lg_context, code, filename)
