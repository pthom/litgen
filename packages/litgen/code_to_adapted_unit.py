from typing import Optional

import srcmlcpp

from litgen.options import LitgenOptions
from litgen.internal.adapted_types.adapted_unit import AdaptedUnit, LitgenWriterContext


def code_to_adapted_unit(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    lg_writer_context: Optional[LitgenWriterContext] = None,
) -> AdaptedUnit:
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code, filename)

    if lg_writer_context is None:
        lg_writer_context = LitgenWriterContext(options)
    adapted_unit = AdaptedUnit(lg_writer_context, cpp_unit)

    return adapted_unit
