"""
Options for srcmlcpp. Read the doc near all options elements.
"""
from __future__ import annotations
from typing import Callable, Optional

from codemanip.code_utils import split_string_by_pipe_char
from srcmlcpp.scrml_warning_settings import WarningType


class SrcmlcppOptions:
    ################################################################################
    #    <API prefixes for functions / API comment suffixes for classes>
    ################################################################################

    # Prefixes that denote exported dll functions.
    # For example, you could use "MY_API" which would be defined as `__declspec(dllexport|dllimport)` on windows
    # You can have several prefixes: separate them with a "|", for example: "MY_API|OTHER_API"
    #
    # If you filled SrcmlcppOptions.functions_api_prefixes, then those prefixes will be mentioned
    # as specifiers for the return type of the functions.
    functions_api_prefixes: str = ""

    ################################################################################
    #    <Numbers parsing: resolve macros values>
    ################################################################################

    # List of named possible numbers or sizes (fill it if some number/sizes are defined by macros or constexpr values)
    # For example it could store `{ "SPACE_DIMENSIONS" : 3 }` if the C++ code uses a macro `SPACE_DIMENSIONS`
    named_number_macros: dict[str, int]

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
    # you need to also fill header_filter_acceptable__regex in order to accept code contained
    # inside header_guards (and other acceptable preprocessor defines you may set via this regex)
    # Your regex can have several options: separate them with a "|".
    # By default, all macros names ending with "_H", "HPP", "HXX" are considered as acceptable.
    header_filter_acceptable__regex: str = "__cplusplus|_h_$|_h$|_H$|_H_$|hpp$|HPP$|hxx$|HXX$"

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

    # List of ignored warnings
    ignored_warnings: list[WarningType]
    # List of ignored warnings, identified by a part of the warning message
    ignored_warning_parts: list[str]

    # Show python callstack when warnings are raised
    flag_show_python_callstack: bool = False

    # if true, display parsing progress during execution (on stdout)
    flag_show_progress: bool = False

    ################################################################################
    # Workaround for https://github.com/srcML/srcML/issues/1833
    ################################################################################
    fix_brace_init_default_value = True

    ################################################################################
    #    <End>
    ################################################################################

    def __init__(self) -> None:
        # See doc for all the params at their declaration site (scroll up!)
        self.named_number_macros = {}
        self.ignored_warnings = []
        self.ignored_warning_parts = []

    def functions_api_prefixes_list(self) -> list[str]:
        assert isinstance(self.functions_api_prefixes, str)
        return split_string_by_pipe_char(self.functions_api_prefixes)


def _int_from_str_or_named_number_macros(options: SrcmlcppOptions, int_str: Optional[str]) -> Optional[int]:
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
