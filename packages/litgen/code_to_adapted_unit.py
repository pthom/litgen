from typing import Optional

import srcmlcpp

from litgen.internal.adapted_types.adapted_unit import AdaptedUnit, LitgenContext


def code_to_adapted_unit(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
) -> AdaptedUnit:
    cpp_unit = srcmlcpp.code_to_cpp_unit(lg_context.options.srcml_options, code, filename)

    adapted_unit = AdaptedUnit(lg_context, cpp_unit)

    return adapted_unit
