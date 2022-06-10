from typing import Callable
from dataclasses import dataclass


@dataclass
class SrcmlOptions:

    #
    # Prefixes that denote functions that should be published (for example ["IMPLOT_API", "IMPLOT_TMP"])
    # if empty, all function are published!
    #
    functions_api_prefixes = []

    # Set header_filter_preprocessor_regions to True if the header has regions like
    #       #ifdef SOME_RARE_OPTION
    #           // code we want to exclude
    #       #endif
    #
    # See srcmlcpp/srcml_filter_preprocessor_regions.py for more complete examples
    #
    # In this case, also fill header_guard_suffixes to exclude header_guards
    #
    header_filter_preprocessor_regions:bool = True
    header_guard_suffixes = ["_H", "HPP", "HXX"]

    # Encoding of python and C++ files
    encoding: str = "utf-8"

    #
    # If you need to preprocess the code before parsing, fill this function
    #
    code_preprocess_function: Callable[[str], str] = None

    #
    # Preserve empty lines, i.e. any empty line in the C++ code will be mentioned as a CppEmptyLine element
    #
    preserve_empty_lines: bool = True

    #
    # Verbose / Quiet mode
    #

    # if quiet, all warning messages are discarded
    flag_quiet: bool = False
    # Show python callstack when warnings are raised
    flag_show_python_callstack: bool = False
