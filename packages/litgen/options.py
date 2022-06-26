from typing import List

from codemanip import code_replacements
from codemanip.code_replacements import StringReplacement

from srcmlcpp import SrcmlOptions


class LitgenOptions:
    """Configuration of the code generation (include / excludes, indentation, c++ to python translation settings, etc.)"""

    #
    # There are interesting options to set in SrcmlOptions (see srcmlcpp/srcml_options.py)
    #
    # Notably:
    # * fill srcml_options.functions_api_prefixes
    #   (the prefixes that denotes the functions that shall be published)
    # * Also, fill the excludes if you encounter issues with some functions or declarations you want to ignore
    srcml_options: SrcmlOptions = SrcmlOptions()

    #
    # Shall the binding show the original location and or signature of elements as a comment
    #
    original_location_flag_show = False
    # if showing location, how many parent folders shall be shown
    # (if -1, show the full path)
    original_location_nb_parent_folders = 0
    # If True, the complete C++ original signature will be show as a comment in the python stub (pyi)
    original_signature_flag_show = False

    #
    # List of code replacements when going from C++ to Python
    # These replacements are applied to type names (for example double -> float, vector-> List, etc)
    # as well as comment (which may contain type names)
    #
    # Note:
    # - by default, code_replacements is prefilled with standard_code_replacements(),
    # - by default, comments_replacements is prefilled with standard_comments_replacements(),
    #
    code_replacements: List[StringReplacement] = []
    comments_replacements: List[StringReplacement] = []

    #
    # Layout settings for the generated python stub code
    #

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

    #
    # Layout settings for the C++ generated pydef code
    #

    # Spacing option in C++ code
    cpp_indent_size: int = 4
    cpp_indent_with_tabs: bool = False

    #
    # enum options
    #

    # Remove the typical "EnumName_" prefix from enum values.
    # For example, with the C enum:
    #     enum MyEnum { MyEnum_A = 0, MyEnum_B };
    # Values would be named "a" and "b" in python
    #
    enum_flag_remove_values_prefix: bool = True
    # Skip count value from enums, for example like in:
    #    enum MyEnum { MyEnum_A = 1, MyEnum_B = 1, MyEnum_COUNT };
    enum_flag_skip_count: bool = True

    ################################################################################
    ################################################################################
    #    <adapt_function_params>
    ################################################################################
    ################################################################################

    #
    # C Buffers to py::array
    #
    # If active, signatures with a C buffer like this:
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

    buffer_flag_replace_by_array = True
    # buffer_types List[str]. Which means that `uint8_t*` are considered as possible buffers
    buffer_types: List[str] = [
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
    ]
    buffer_template_types: List[str] = [
        "T"
    ]  # Which means that templated functions using a buffer use T as a templated name
    buffer_size_names: List[str] = ["nb", "size", "count", "total", "n"]

    #
    # C style arrays functions and methods parameters
    #
    # If c_array_const_flag_replace is active, then signatures like
    #       void foo_const(const int input[2])
    # will be transformed to:
    #       void foo_const(const std::array<int, 2>& input)
    #
    # If c_array_modifiable_flag_replace is active, then signatures like
    #       void foo_non_const(int output[2])
    # will be transformed to:
    #       void foo_non_const(BoxedInt & output_0, BoxedInt & output_1)
    # (c_array_modifiable_max_size is the maximum number of params that can be boxed like this)
    #
    c_array_const_flag_replace = True
    c_array_modifiable_flag_replace = True
    c_array_modifiable_max_size = 10

    # If c_string_list_flag_replace is active, then C string lists `(const char **, size_t)`
    # will be replaced by `const std::vector<std::string>&`. For example:
    #     void foo(const char * const items[], int items_count)
    # will be transformed to:
    #     void foo(const std::vector<std::string>& const items[])
    c_string_list_flag_replace = True

    """
    We want to adapt functions params that use modifiable pointer or reference to a type that is immutable in python.
    For example
        int foo(int* value)
    From python, the adapted signature will be:
        def foo(BoxedInt value) -> int
    So that modification done on the C++ side can be seen from python.
    """
    fn_params_adapt_modifiable_immutable = True

    ################################################################################
    ################################################################################
    #    </adapt_function_params>
    ################################################################################
    ################################################################################

    # Force using py::overload for functions that matches these regexes
    fn_force_overload_regexes: List[str] = []
    # If true, all functions that returns pointers will have the policy `pybind11::return_value_policy::reference)`
    fn_force_return_policy_reference_for_pointers: bool = False
    fn_force_return_policy_reference_for_references: bool = False

    #
    # C style arrays structs and class members
    #
    # If c_array_numeric_member_flag_replace is active, then members like
    #       struct Foo {  int values[10]; };
    # will be transformed to a property that points to a numpy array
    # which can be read/written from python (this requires numpy)
    c_array_numeric_member_flag_replace = True
    # list of numeric types that can be stored in a numpy array
    c_array_numeric_member_types = [  # don't include char !
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

    #
    # Options that need rework
    #
    # Shall we generate a __str__() method for structs
    generate_to_string: bool = False
    # Function that may generate additional code in the function defined in the  __init__.py file of the package
    # poub_init_function_python_additional_code: Optional[Callable[[FunctionsInfos], str]]

    #
    # Sanity checks and utilities below
    #
    def assert_buffer_types_are_ok(self) -> None:
        # the only authorized type are those for which the size is known with certainty
        # * int and long are not acceptable candidates: use int8_t, uint_8t, int32_t, etc.
        # * concerning float and doubles, there is no standard for fixed size floats, so we have to cope with
        #   float, double and long double and their various platforms implementations...
        authorized_types = [
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
        ]
        for buffer_type in self.buffer_types:
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
