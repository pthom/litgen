from typing import Callable, Dict, List, Optional


class SrcmlOptions:

    #
    # Prefixes that denote functions that should be published (for example ["IMPLOT_API"])
    # if empty, all function are published!
    #
    functions_api_prefixes: List[str] = []

    #
    # Suffixes that denote structs, classes, enums and namespaces that should be published, for example:
    #       struct MyStruct        // IMMVISION_API_STRUCT     <== this is a suffix
    #       { };
    # if empty, all structs/enums/classes/namespaces are published
    #
    # you may decide to fill api_suffixes and functions_api_prefixes with the same value(s)
    api_suffixes: List[str] = []

    #
    # Excludes
    #

    # Exclude certain functions and methods by a regex on their name
    # These are regexes. If you want to exclude an exact function name, use a regex like this:
    #         r"\bYourFunctionName\b",
    function_name_exclude_regexes: List[str] = []
    # Exclude certain declarations, (namespace variables, struct and class members) by a regex on their name
    decl_name_exclude_regexes: List[str] = []
    # Exclude certain classes and structs by a regex on their name
    class_name_exclude_regexes: List[str] = []
    # Exclude certain declarations (mainly class members) based on their type
    decl_types_exclude_regexes: List[str] = []

    #
    # List of named possible numbers or sizes (fill it if some number/sizes are defined by macros or constexpr values)
    # For example it could store `{ "SPACE_DIMENSIONS" : 3 }` if the C++ code uses a macro `SPACE_DIMENSIONS`
    named_number_macros: Dict[str, int] = {}

    #
    # Header cleaning
    #
    # Set header_filter_preprocessor_regions to True if the header has regions like
    #       #ifdef SOME_RARE_OPTION
    #           // code we want to exclude
    #       #endif
    #
    # See srcmlcpp/srcml_filter_preprocessor_regions.py for more complete examples
    #
    # In this case, also fill header_guard_suffixes to exclude header_guards
    #
    header_filter_preprocessor_regions: bool = True
    header_guard_suffixes = ["_H", "HPP", "HXX"]

    # Encoding of python and C++ files
    encoding: str = "utf-8"

    #
    # If you need to preprocess the code before parsing, fill this function
    #
    code_preprocess_function: Optional[Callable[[str], str]] = None

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

    def __init__(self) -> None:
        self.api_suffixes = []
        self.functions_api_prefixes = []
        self.named_number_macros = {}
        self.code_preprocess_function = None
