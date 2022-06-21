from typing import List, Optional, Union

from codemanip import code_utils
from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_types import *
from litgen.options import LitgenOptions
from srcmlcpp.srcml_types import *


def generate_pyi(
    cpp_unit: Union[CppUnit, CppBlock],
    options: LitgenOptions,
    current_namespaces: List[str] = [],
    add_boxed_types_definitions: bool = False,
) -> str:

    adapted_block = AdaptedBlock(cpp_unit, options)
    block_code = adapted_block.str_stub()

    if add_boxed_types_definitions:
        pass

    code = block_code

    code = code_utils.code_set_max_consecutive_empty_lines(code, options.python_max_consecutive_empty_lines)

    # if options.python_run_black_formatter
    #     ...

    return code
