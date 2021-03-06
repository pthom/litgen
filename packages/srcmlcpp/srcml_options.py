"""
Options for srcmlcpp. Read the doc near all options elements.
"""
from typing import Callable, Dict, List, Optional


class SrcmlOptions:

    ################################################################################
    #    <API prefixes for functions / API comment suffixes for classes>
    ################################################################################

    # Prefixes that denote functions that should be published (for example ["IMPLOT_API"])
    # if empty, all function are published!
    #
    functions_api_prefixes: List[str] = []

    # Suffixes that denote structs, classes, enums and namespaces that should be published, for example:
    #       struct MyStruct        // IMMVISION_API_STRUCT     <== this is a suffix
    #       { };
    # if empty, all structs/enums/classes/namespaces are published
    #
    # you may decide to fill api_suffixes and functions_api_prefixes with the same value(s)
    api_suffixes: List[str] = []

    ################################################################################
    #    <Numbers parsing: resolve macros values>
    ################################################################################

    # List of named possible numbers or sizes (fill it if some number/sizes are defined by macros or constexpr values)
    # For example it could store `{ "SPACE_DIMENSIONS" : 3 }` if the C++ code uses a macro `SPACE_DIMENSIONS`
    named_number_macros: Dict[str, int] = {}

    ################################################################################
    #    <Exclude certain regions based on preprocessor macros>
    ################################################################################

    # Set header_filter_preprocessor_regions to True if the header has regions like
    #       #ifdef SOME_RARE_OPTION
    #           // code we want to exclude
    #       #endif
    #
    # See srcmlcpp/filter_preprocessor_regions.py for more complete examples
    #
    # In this case, also fill header_guard_suffixes to exclude header_guards
    #
    header_filter_preprocessor_regions: bool = True
    header_guard_suffixes = ["_H", "HPP", "HXX"]

    ################################################################################
    #    <Custom preprocess of the code>
    ################################################################################

    #
    # If you need to preprocess the code before parsing, fill this function
    #
    code_preprocess_function: Optional[Callable[[str], str]] = None

    ################################################################################
    #    <Misc options>
    ################################################################################

    # Encoding of python and C++ files
    encoding: str = "utf-8"

    # Preserve empty lines, i.e. any empty line in the C++ code will be mentioned as a CppEmptyLine element
    # this is done by adding a dummy comment on the line.
    preserve_empty_lines: bool = True

    # srcml_dump_positions: if True, code positions will be outputted in the xml tree (recommended)
    srcml_dump_positions: bool = True

    ################################################################################
    #    <Verbose / Quiet mode>
    ################################################################################

    # if quiet, all warning messages are discarded
    flag_quiet: bool = False

    # Show python callstack when warnings are raised
    flag_show_python_callstack: bool = False

    ################################################################################
    #    <End>
    ################################################################################

    def __init__(self) -> None:
        self.api_suffixes = []
        self.functions_api_prefixes = []
        self.named_number_macros = {}
        self.code_preprocess_function = None


def _int_from_str_or_named_number_macros(options: SrcmlOptions, int_str: Optional[str]) -> Optional[int]:
    if int_str is None:
        return None

    try:
        v = int(int_str)
        return v
    except ValueError:
        if int_str in options.named_number_macros:
            return options.named_number_macros[int_str]
        else:
            return None
