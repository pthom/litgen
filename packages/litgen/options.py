from typing import List

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
    srcml_options: SrcmlOptions

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
    # as well as comment (which may contain type names), and function/member names
    #
    # Note:
    # - by default, code_replacements is prefilled with standard_code_replacements()
    # - by default, comments_replacements is prefilled with standard_comments_replacements()
    # - by default, names_replacements is empty
    code_replacements: RegexReplacementList  # = cpp_to_python.standard_code_replacements() by default
    comments_replacements: RegexReplacementList  # = cpp_to_python.standard_comment_replacements() by default
    names_replacements: RegexReplacementList  # = RegexReplacementList() by default (i.e. empty)

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

    #
    # ------------------------------------------------------------------------------
    # Note about regexes below:
    # =========================
    # - regexes can support several alternatives: separate them by "|"
    # For example, in order to match an exact function name, as well as functions ending with "_private",
    # use a regex like this:
    #         r"^YourFunctionName$|_private$",
    # - If a regex string is empty, it will not match anything
    # - To match everything, use r".*"
    # - It is advised to prefix your regex expressions with "r" (in order to use raw strings)
    # ------------------------------------------------------------------------------
    #

    # Exclude certain functions and methods by a regex on their name
    fn_exclude_by_name__regex: str = ""

    # ------------------------------------------------------------------------------
    # C style buffers to py::array
    # ------------------------------------------------------------------------------
    #
    # Signatures with a C buffer like this:
    #       MY_API inline void add_inside_array(uint8_t* array, size_t array_size, uint8_t number_to_add)
    # may be transformed to:
    #       void add_inside_array(py::array & array, uint8_t number_to_add)              (c++ bound signature)
    #       def add_inside_array(array: numpy.ndarray, number_to_add: int) -> None       (python)
    #
    # It also works for templated buffers:
    #       MY_API template<typename T> void mul_inside_array(T* array, size_t array_size, double factor)
    # will be transformed to:
    #       void mul_inside_array(py::array & array, double factor)                      (c++ bound signature)
    #       def mul_inside_array(array: numpy.ndarray, factor: float) -> None            (python)
    # (and factor will be down-casted to the target type)
    #
    # fn_params_buffer_replace_by_array_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to r".*" to apply this to all functions (which is the default), set it to "" to disable it
    #
    fn_params_replace_buffer_by_array__regex: str = r".*"

    # fn_params_buffer_types: list of numeric types that are considered as possible buffers.
    # You can customize this list in your own options by removing items from it,
    # but you *cannot* add new types or new synonyms (typedef for examples); since the conversion between
    # py::array and native relies on these *exact* names!
    #
    # By default, fn_params_buffer_types will contain:
    #      [
    #         "uint8_t",
    #         "int8_t",
    #         "uint16_t",
    #         "int16_t",
    #         "uint32_t",
    #         "int32_t",
    #         "uint64_t",
    #         "int64_t",
    #         "float",
    #         "double",
    #         "long double",
    #         "long long",
    #     ]
    fn_params_buffer_types: List[str]

    # fn_params_buffer_template_types: list of templated names that are considered as possible templated buffers
    fn_params_buffer_template_types: List[str]  # = ["T", "NumericType"] by default

    # fn_params_buffer_size_names: possible names for the size of the buffer
    fn_params_buffer_size_names: List[str]  # = ["nb", "size", "count", "total", "n"] by default

    # ------------------------------------------------------------------------------
    # C style arrays functions and methods parameters
    # ------------------------------------------------------------------------------
    #
    # Signatures like
    #       void foo_const(const int input[2])
    # may be transformed to:
    #       void foo_const(const std::array<int, 2>& input)    (c++ bound signature)
    #       def foo_const(input: List[int]) -> None:           (python)
    # fn_params_buffer_replace_by_array_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to r".*" to apply this to all functions, set it to "" to disable it
    fn_params_replace_const_c_array_by_std_array__regex: str = r".*"

    # Signatures like
    #       void foo_non_const(int output[2])
    # may be transformed to:
    #       void foo_non_const(BoxedInt & output_0, BoxedInt & output_1)         (c++ bound signature)
    #       def foo_non_const(output_0: BoxedInt, output_0: BoxedInt) -> None    (python)
    # fn_params_replace_modifiable_c_array_by_boxed__regex contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to r".*" to apply this to all functions, set it to "" to disable it
    fn_params_replace_modifiable_c_array_by_boxed__regex: str = r".*"
    # (c_array_modifiable_max_size is the maximum number of params that can be boxed like this)
    fn_params_replace_modifiable_c_array__max_size = 10

    # ------------------------------------------------------------------------------
    # C style string list functions and methods parameters
    # ------------------------------------------------------------------------------
    # Signatures like
    #     void foo(const char * const items[], int items_count)
    # may be transformed to:
    #     void foo(const std::vector<std::string>& const items[])        (c++ bound signature)
    #     def foo(items: List[str]) -> None                              (python)
    # fn_params_replace_c_string_list_regexes contains a list of regexes on functions names
    # for which this transformation will be applied.
    # Set it to [r".*"] to apply this to all functions, set it to [] to disable it
    fn_params_replace_c_string_list__regex: str = r".*"

    # ------------------------------------------------------------------------------
    # Make "immutable python types" modifiable, when passed by pointer or reference
    # ------------------------------------------------------------------------------
    #
    # adapt functions params that use non const pointers or reference to a type that is immutable in python.

    # Signatures like
    #     int foo(int* value)
    # May be transformed to:
    #     def foo(BoxedInt value) -> int                                  (python)
    # So that any modification done on the C++ side can be seen from python.
    #
    # fn_params_adapt_modifiable_immutable_regexes contains a list of regexes on functions names
    # Set it to r".*" to apply this to all functions. Set it to "" to disable it
    fn_params_replace_modifiable_immutable_by_boxed__regex: str = ""

    # As an alternative, we can also add the modified value to the returned type
    # of the function (which will now be a tuple)
    #
    # For example
    #     int foo(int* value)
    # May be transformed to:
    #     def foo(int value) -> Tuple[int, bool]
    # So that any modification done on the C++ side can be seen from python.
    #
    # fn_params_output_modifiable_immutable_to_return__regex contains a list of regexes on functions names
    # Set it to r".*" to apply this to all functions. Set it to "" to disable it
    fn_params_output_modifiable_immutable_to_return__regex: str = ""

    # ------------------------------------------------------------------------------
    # Exclude some params by name
    # ------------------------------------------------------------------------------
    #
    # Remove some params from the python published interface. A param can only be removed if it has a default value
    # in the C++ signature
    fn_params_exclude_names__regex: str = ""
    fn_params_exclude_types__regex: str = ""

    # ------------------------------------------------------------------------------
    # Force overload
    # ------------------------------------------------------------------------------
    # Force using py::overload for functions that matches these regexes
    fn_force_overload__regex: str = ""

    # ------------------------------------------------------------------------------
    # Return policy
    # ------------------------------------------------------------------------------
    # Force the function that match those regexes to use `pybind11::return_value_policy::reference)`
    # (Note: you can also write "// return_value_policy::reference" as an end of line comment after the function:
    #  see packages/litgen/integration_tests/mylib/include/mylib/return_value_policy_test.h as an example)
    fn_return_force_policy_reference_for_pointers__regex: str = ""
    fn_return_force_policy_reference_for_references__regex: str = ""

    ################################################################################
    #    <class and struct member adaptations>
    ################################################################################

    # Exclude certain classes and structs by a regex on their name
    class_exclude_by_name__regex: str = ""

    # Exclude certain members by a regex on their name
    member_exclude_by_name__regex: str = ""

    # Exclude members based on their type
    member_exclude_by_type__regex: str = ""

    # adapt class members which are a fixed size array of a numeric type:
    #
    # For example
    #       struct Foo {  int values[10]; };
    # May be transformed to:
    #       class Foo:
    #           values: numpy.ndarray
    #
    # i.e. the member will be transformed to a property that points to a numpy array
    # which can be read/written from python (this requires numpy)
    # This is active by default.
    member_numeric_c_array_replace__regex: str = r".*"

    # member_numeric_c_array_types: list of numeric types that can be stored in a numpy array
    #
    #     See https://numpy.org/doc/stable/reference/generated/numpy.chararray.html
    #     *don't* include char, *don't* include byte, those are not numeric!
    #
    # by default:
    # member_numeric_c_array_types = [
    #     "int",
    #     "unsigned int",
    #     "long",
    #     "unsigned long",
    #     "long long",
    #     "unsigned long long",
    #     "float",
    #     "double",
    #     "long double",
    #     "uint8_t",
    #     "int8_t",
    #     "uint16_t",
    #     "int16_t",
    #     "uint32_t",
    #     "int32_t",
    #     "uint64_t",
    #     "int64_t",
    #     "bool",
    # ]
    member_numeric_c_array_types: List[str]

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
        # See doc for all the params at their declaration site (scroll up to the top of this file!)
        from litgen.internal import cpp_to_python

        self.srcml_options = SrcmlOptions()
        self.srcml_options.header_filter_preprocessor_regions = True

        self.code_replacements = cpp_to_python.standard_code_replacements()
        self.comments_replacements = cpp_to_python.standard_comment_replacements()
        self.names_replacements = RegexReplacementList()
        # See doc for all the params at their declaration site (scroll up to the top of this file!)
        self.fn_params_buffer_types = [
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
        # See doc for all the params at their declaration site (scroll up!)
        self.fn_params_buffer_template_types = ["T", "NumericType"]
        self.fn_params_buffer_size_names = ["nb", "size", "count", "total", "n"]
        # See doc for all the params at their declaration site (scroll up to the top of this file!)
        self.member_numeric_c_array_types = [  # don't include char, don't include byte, those are not numeric!
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
