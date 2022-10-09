"""
Options for srcmlcpp. Read the doc near all options elements.
"""
from typing import Callable, Dict, List, Optional
from codemanip.code_utils import split_string_by_pipe_char


class SrcmlOptions:

    ################################################################################
    #    <API prefixes for functions / API comment suffixes for classes>
    ################################################################################

    # Prefixes that denote exported dll functions.
    # For example, you could use "MY_API" which would be defined as `__declspec(dllexport|dllimport)` on windows
    # You can have several prefixes: separate them with a "|", for example: "MY_API|OTHER_API"
    #
    # If you filled SrcmlOptions.functions_api_prefixes, then those prefixes will be mentioned
    # as specifiers for the return type of the functions.
    functions_api_prefixes: str = ""

    ################################################################################
    #    <Numbers parsing: resolve macros values>
    ################################################################################

    # List of named possible numbers or sizes (fill it if some number/sizes are defined by macros or constexpr values)
    # For example it could store `{ "SPACE_DIMENSIONS" : 3 }` if the C++ code uses a macro `SPACE_DIMENSIONS`
    named_number_macros: Dict[str, int]

    ################################################################################
    #    <Exclude certain regions based on preprocessor macros>
    ################################################################################

    # Set header_filter_preprocessor_regions to True if the header has regions
    # that you want to exclude from the parsing, like this:
    #       #ifdef SOME_RARE_OPTION
    #           // code we want to exclude
    #       #endif
    #
    # See srcmlcpp/filter_preprocessor_regions.py for more complete examples
    header_filter_preprocessor_regions: bool = False
    # If header_filter_preprocessor_regions is True,
    # you need to also fill header_filter_acceptable_suffixes in order to accept code contained inside header_guards
    # and other acceptable preprocessor defines.
    # You can have several suffixes: separate them with a "|", for example: "_H|_HPP|MY_ACCEPTABLE_MACRO"
    # By default, all macros names ending with "_H", "HPP", "HXX" are considered as header guards.
    header_filter_acceptable_suffixes: str = "_H|HPP|HXX"

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

    # flag_srcml_dump_positions: if True, code positions will be outputted in the xml tree (recommended)
    flag_srcml_dump_positions: bool = True

    # indentation used by CppElements str_code() methods (4 spaces by default)
    indent_cpp_str: str = "    "

    ################################################################################
    #    <Verbose / Quiet mode>
    ################################################################################

    # if quiet, all warning messages are discarded (warning messages go to stderr)
    flag_quiet: bool = False

    # Show python callstack when warnings are raised
    flag_show_python_callstack: bool = False

    # if true, display parsing progress during execution (on stdout)
    flag_show_progress: bool = False

    ################################################################################
    #    <End>
    ################################################################################

    def __init__(self) -> None:
        # See doc for all the params at their declaration site (scroll up!)
        self.named_number_macros = {}

    def functions_api_prefixes_list(self) -> List[str]:
        return split_string_by_pipe_char(self.functions_api_prefixes)

    def header_filter_acceptable_suffixes_list(self) -> List[str]:
        return split_string_by_pipe_char(self.header_filter_acceptable_suffixes)


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
