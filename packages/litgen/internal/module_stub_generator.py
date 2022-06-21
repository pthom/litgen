from typing import List, Union

from codemanip import code_utils

from srcmlcpp.srcml_types import *

from litgen.internal.adapted_types import *
from litgen.options import LitgenOptions


def generate_stub(
    options: LitgenOptions,
    cpp_unit: Union[CppUnit, CppBlock],
    current_namespaces: List[str] = [],
    add_boxed_types_definitions: bool = False,
) -> str:

    adapted_block = AdaptedBlock(options, cpp_unit)
    block_code = adapted_block.str_stub()

    if add_boxed_types_definitions:
        pass

    code = block_code

    code = code_utils.code_set_max_consecutive_empty_lines(code, options.python_max_consecutive_empty_lines)

    # if options.python_run_black_formatter
    #     ...

    return code
