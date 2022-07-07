from typing import List

from codemanip import code_replacements
from codemanip.code_replacements import RegexReplacementList

from srcmlcpp import SrcmlOptions


class LitgenOptions:
    """Numerous options to configure litgen code generation.

    (include / excludes, indentation, c++ to python translation settings, function parameters
    adaptations, etc.)"""

    ################################################################################
    #    <srcmlcpp options>
    ################################################################################
    # There are interesting options to set in SrcmlOptions (see srcmlcpp/srcml_options.py)
    #
    # Notably:
    # * fill srcml_options.functions_api_prefixes
    #   (the prefixes that denotes the functions that shall be published)
    # * Also, fill the excludes if you encounter issues with some functions or declarations you want to ignore
    srcml_options: SrcmlOptions = SrcmlOptions()

    ################################################################################
    #    <show the original location and or signature of elements as a comment>
    ################################################################################
    original_location_flag_show = False
    # if showing location, how many parent folders shall be shown
    # (if -1, show the full path)
    original_location_nb_parent_folders = 0
    # If True, the complete C++ original signature will be show as a comment in the python stub (pyi)
    original_signature_flag_show = False

    ################################################################################
    #    <Type names translation from C++ to python>
    ################################################################################
    # List of code replacements when going from C++ to Python
    # These replacements are applied to type names (for example double -> float, vector-> List, etc)
    # as well as comment (which may contain type names)
    #
    # Note:
    # - by default, code_replacements is prefilled with standard_code_replacements(),
    # - by default, comments_replacements is prefilled with standard_comments_replacements(),
    #
    code_replacements: RegexReplacementList = RegexReplacementList()
    comments_replacements: RegexReplacementList = RegexReplacementList()

    ################################################################################
    #    <Layout settings for the generated python stub code>
    ################################################################################
    # Convert variables and functions names to snake_case (class, structs, and enums names are always preserved)
    python_convert_to_snake_case: bool = True
    # Size of an indentation in the python stubs
    python_indent_size = 4
    python_ident_with_tabs: bool = False
    # Insert as many empty lines in the python stub as found in the header file, keep comments layout, etc.
    python_reproduce_cpp_layout: bool = True
    # Reformat the generated python to remove long series of empty lines (disabled if < 0)
    python_max_consecutive_empty_lines: int = -1
    # The generated code will try to adhere to this max length (if negative, this is ignored)
    python_max_line_length = 80
    # Strip (remove) empty comment lines
    python_strip_empty_comment_lines: bool = False
    # Run black formatter
    python_run_black_formatter: bool = False
    python_black_formatter_line_length: int = 88

    ################################################################################
    #    <Layout settings for the C++ generated pydef code>
    ################################################################################
    # Spacing option in C++ code
    cpp_indent_size: int = 4
    cpp_indent_with_tabs: bool = False

    ################################################################################
    #    <enum adaptations>
    ################################################################################
    # Remove the typical "EnumName_" prefix from enum values.
    # For example, with the C enum:
    #     enum MyEnum { MyEnum_A = 0, MyEnum_B };
    # Values would be named "a" and "b" in python
    enum_flag_remove_values_prefix: bool = True
    # Skip count value from enums, for example like in:
    #    enum MyEnum { MyEnum_A = 1, MyEnum_B = 1, MyEnum_COUNT };
    enum_flag_skip_count: bool = True

    ################################################################################
    #    <functions and method adaptations>
    ################################################################################

    # Exclude certain functions and methods by a regex on their name
    # These are regexes. If you want to exclude an exact function name, use a regex like this:
    #         r"^YourFunctionName$",
    fn_exclude_by_name__regexes: List[str] = []

    # C Buffers to py::array
    #
    # If fn_params_replace_buffer_by_array__regexes matches, then signatures with a C buffer like this:
    #       MY_API inline void add_inside_array(uint8_t* array, size_t array_size, uint8_t number_to_add)
    # will be transformed to:
    #       void add_inside_array(py::array & array, uint8_t number_to_add)
    #
    # It also works for templated buffers:
    #       MY_API template<typename T> void mul_inside_array(T* array, size_t array_size, double factor)
    # will be transformed to:
    #       void mul_inside_array(py::array & array, double factor)
    # (and factor will be down-casted to the target type)
    #
    # fn_params_buffer_replace_by_array_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to [r".*"] to apply this to all functions (which is the default), set it to [] to disable it
    #
    fn_params_replace_buffer_by_array__regexes: List[str] = [r".*"]

    # buffer_types List[str]. Which means that `uint8_t*` are considered as possible buffers
    # You can customize this list in your own options by removing items from it,
    # but you *cannot* add new types or new synonyms (typedef for examples); since the conversion between
    # py::array and native relies on these exact names!
    fn_params_buffer_types: List[str] = [
        "uint8_t",
        "int8_t",
        "uint16_t",
        "int16_t",
        "uint32_t",
        "int32_t",
        "uint64_t",
        "int64_t",
        "float",
        "double",
        "long double",
        "long long",
    ]
    fn_params_buffer_template_types: List[str] = [
        "T"
    ]  # Which means that templated functions using a buffer use T as a templated name
    fn_params_buffer_size_names: List[str] = ["nb", "size", "count", "total", "n"]

    #
    # C style arrays functions and methods parameters
    #
    # If active, then signatures like
    #       void foo_const(const int input[2])
    # will be transformed to:
    #       void foo_const(const std::array<int, 2>& input)
    #
    # fn_params_buffer_replace_by_array_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to [r".*"] to apply this to all functions, set it to [] to disable it
    fn_params_replace_const_c_array_by_std_array__regexes: List[str] = [".*"]

    # If c_array_modifiable_flag_replace is active, then signatures like
    #       void foo_non_const(int output[2])
    # will be transformed to:
    #       void foo_non_const(BoxedInt & output_0, BoxedInt & output_1)
    # (c_array_modifiable_max_size is the maximum number of params that can be boxed like this)
    #
    # fn_params_replace_modifiable_c_array_by_boxed__regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to [r".*"] to apply this to all functions, set it to [] to disable it
    fn_params_replace_modifiable_c_array_by_boxed__regexes: List[str] = [".*"]
    fn_params_replace_modifiable_c_array__max_size = 10

    # If c_string_list_flag_replace is active, then C string lists `(const char **, size_t)`
    # will be replaced by `const std::vector<std::string>&`. For example:
    #     void foo(const char * const items[], int items_count)
    # will be transformed to:
    #     void foo(const std::vector<std::string>& const items[])
    #
    # fn_params_replace_c_string_list_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to [r".*"] to apply this to all functions, set it to [] to disable it
    fn_params_replace_c_string_list__regexes: List[str] = [r".*"]

    # fn_params_adapt_modifiable_immutable:
    # adapt functions params that use non cont pointers or reference to a type that is immutable in python.
    #
    # For example
    #     int foo(int* value)
    # From python, the adapted signature will be:
    #     def foo(BoxedInt value) -> int
    #
    # So that any modification done on the C++ side can be seen from python.
    #
    # fn_params_adapt_modifiable_immutable_regexes contains a list of regexes on functions names
    # Set it to [r".*"] to apply this to all functions. Set it to [] to disable it
    fn_params_replace_modifiable_immutable_by_boxed__regexes: List[str] = []

    # fn_params_adapt_modifiable_immutable_to_return_regexes:
    # adapt functions params that use non const pointers or reference to a type that is immutable in python
    # by adding the modified value to the returned type of the function (which will now be a tuple)
    #
    # For example
    #     int foo(int* value)
    # From python, the adapted signature will be:
    #     def foo(int value) -> Tuple[int, bool]
    #
    # So that any modification done on the C++ side can be seen from python.
    #
    # fn_params_output_modifiable_immutable_to_return__regexes contains a list of regexes on functions names
    # Set it to [r".*"] to apply this to all functions. Set it to [] to disable it
    fn_params_output_modifiable_immutable_to_return__regexes: List[str] = []

    # Remove some params from the python published interface. A param can only be removed if it has a default value
    # in the C++ signature
    fn_params_exclude_names__regexes: List[str] = []
    fn_params_exclude_types__regexes: List[str] = []

    # Force using py::overload for functions that matches these regexes
    fn_force_overload__regexes: List[str] = []

    # If true, all functions that returns pointers will have the policy `pybind11::return_value_policy::reference)`
    fn_return_force_policy_reference_for_pointers__regexes: List[str] = []
    fn_return_force_policy_reference_for_references__regexes: List[str] = []

    ################################################################################
    #    <class and struct member adaptations>
    ################################################################################

    # Exclude certain classes and structs by a regex on their name
    class_exclude_by_name__regexes: List[str] = []

    # Exclude certain members by a regex on their name
    member_exclude_by_name__regexes: List[str] = []

    # Exclude members based on their type
    member_exclude_by_type__regexes: List[str] = []

    # If member_numeric_c_array_replace__regexes matchs, then members like
    #       struct Foo {  int values[10]; };
    # will be transformed to a property that points to a numpy array
    # which can be read/written from python (this requires numpy)
    member_numeric_c_array_replace__regexes: List[str] = [r".*"]

    # list of numeric types that can be stored in a numpy array
    member_numeric_c_array_types = [  # don't include char, don't include byte, those are not numeric!
        "int",  # See https://numpy.org/doc/stable/reference/generated/numpy.chararray.html
        "unsigned int",
        "long",
        "unsigned long",
        "long long",
        "unsigned long long",
        "float",
        "double",
        "long double",
        "uint8_t",
        "int8_t",
        "uint16_t",
        "int16_t",
        "uint32_t",
        "int32_t",
        "uint64_t",
        "int64_t",
        "bool",
    ]

    ################################################################################
    #    <unclassified options>
    ################################################################################
    # Shall we generate a __str__() method for structs / Work in progress!
    generate_to_string: bool = False

    ################################################################################
    #    <Sanity checks and utilities below>
    ################################################################################
    def check_options_consistency(self) -> None:
        # the only authorized type are those for which the size is known with certainty
        # * int and long are not acceptable candidates: use int8_t, uint_8t, int32_t, etc.
        # * concerning float and doubles, there is no standard for fixed size floats, so we have to cope with
        #   float, double and long double and their various platforms implementations...
        authorized_types = [
            "byte",
            "uint8_t",
            "int8_t",
            "uint16_t",
            "int16_t",
            "uint32_t",
            "int32_t",
            "uint64_t",
            "int64_t",
            "float",
            "double",
            "long double",
            "long long",
        ]
        for buffer_type in self.fn_params_buffer_types:
            if buffer_type not in authorized_types:
                raise ValueError(
                    f"""
                    options.build_types contains an unauthorized type: {buffer_type}
                    Authorized types are: { ", ".join(authorized_types) }
                    """
                )

    def indent_cpp_spaces(self) -> str:
        space = "\t" if self.cpp_indent_with_tabs else " "
        return space * self.cpp_indent_size

    def indent_python_spaces(self) -> str:
        space = "\t" if self.python_ident_with_tabs else " "
        return space * self.python_indent_size

    def __init__(self) -> None:
        from litgen.internal import cpp_to_python

        self.srcml_options = SrcmlOptions()
        self.code_replacements = cpp_to_python.standard_code_replacements()
        self.comments_replacements = cpp_to_python.standard_comment_replacements()
