from typing import Optional

import srcmlcpp

from litgen.options import LitgenOptions
from litgen.internal.adapted_types.adapted_unit import AdaptedUnit


def code_to_adapted_unit(
    options: LitgenOptions, code: Optional[str] = None, filename: Optional[str] = None
) -> AdaptedUnit:
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code, filename)
    adapted_unit = AdaptedUnit(options, cpp_unit)
    return adapted_unit
