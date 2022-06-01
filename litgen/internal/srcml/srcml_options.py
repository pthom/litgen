from typing import Callable
from dataclasses import dataclass


@dataclass
class SrcmlOptions:
    header_filter_preprocessor_regions:bool = True
    encoding: str = "utf-8"
    code_preprocess_function: Callable[[str], str] = None

    header_guard_suffixes = ["_H", "HPP", "HXX"]

    # Preserve empty lines, i.e. any empty line in the C++ code will be mentioned as a CppEmptyLine element
    preserve_empty_lines: bool = True

    # Prefixes that denote functions that should be published (for example ["IMPLOT_API", "IMPLOT_TMP"])
    # if empty, all function are published!
    functions_api_prefixes = []

    # if quiet, all warning messages are discarded
    flag_quiet: bool = False
    # Show python callstack when warnings are raised
    flag_show_python_callstack: bool = False
