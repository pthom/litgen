from dataclasses import dataclass, field
from typing import List

from litgen.internal.code_utils import make_regex_any_variable_ending_with, make_regex_any_variable_starting_with
from srcmlcpp import SrcmlOptions


def _preprocess_imgui_code(code):
    import re
    new_code = code
    new_code  = re.sub(r'IM_FMTARGS\(\d\)', '', new_code)
    new_code  = re.sub(r'IM_FMTLIST\(\d\)', '', new_code)
    return new_code


@dataclass
class CodeStyleOptions:

    #
    # There are interesting options to set in SrcmlOptions (see srcmlcpp/srcml_options.py)
    #
    # Notably, fill srcml_options.functions_api_prefixes
    # (the prefixes that denotes the functions that shall be published)
    #
    srcml_options: SrcmlOptions = SrcmlOptions()

    #
    # Shall the binding cpp file show the original location of elements as a comment
    #
    flag_show_original_location_in_pybind_file = False

    #
    # Exclude certain functions by a regex on their name
    #
    function_name_exclude_regexes: List[str] = field(default_factory=list)
    # Exclude functions by adding a comment on the same line of their declaration
    function_exclude_by_comment: List[str] = field(default_factory=list)

    #
    # List of code replacements when going from C++ to Python
    # These replacements are applied to type names (for example double -> float, vector-> List, etc)
    # as well as comment (which may contain type names)
    #
    # Note: you can prefill it with litgen.standard_replacements()
    #
    code_replacements = [] # List[StringReplacement]

    #
    # Indentation settings for the generated code
    #

    # Size of an indentation in the python stubs
    indent_python_size = 4
    # Spacing option in C++ code
    indent_cpp_size: int = 4
    indent_cpp_with_tabs: bool = False

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
    buffer_flag_replace_by_array = False
    buffer_types = ["int8_t", "uint8_t"] # of type List[str]. Which means that `uint8_t*` are considered as possible buffers
    buffer_template_types = ["T"] # Which means that templated functions using a buffer use T as a templated name
    buffer_size_regexes = [
        make_regex_any_variable_ending_with("count"),   # any variable name ending with count or Count
        make_regex_any_variable_starting_with("count"), # any variable name starting with count or Count
        make_regex_any_variable_ending_with("size"),
        make_regex_any_variable_starting_with("size"),
    ]

    #
    # C style arrays processing
    #
    # if c_array_const_flag_replace is active, then signatures like
    #       void foo_const(const int input[2])
    # will be transformed to:
    #       void foo_const(const std::array<int, 2>& input)
    #
    # if c_array_modifiable_flag_replace is active, then signatures like
    #       void foo_non_const(int output[2])
    # will be transformed to:
    #       void foo_non_const(BoxedInt & output_0, BoxedInt & output_1)
    # (c_array_modifiable_max_params is the maximum number of params that can be boxed like this)
    #
    c_array_const_flag_replace = False
    c_array_modifiable_flag_replace = False
    c_array_modifiable_max_params = 10

    #
    # Options that need rework
    #
    # Shall we generate a __str__() method for structs
    generate_to_string: bool = False
    # Function that may generate additional code in the function defined in the  __init__.py file of the package
    poub_init_function_python_additional_code = None # Callable[[FunctionsInfos], str]


    #
    # Sanity checks and utilities below
    #
    def assert_buffer_types_are_ok(self):
        # the only authorized type are those for which the size is known with certainty
        # (except for float, double and long double for which there seems to be no reliable standard)
        authorized_types = [
            'uint8_t',
            'int8_t',
            'uint16_t',
            'int16_t',
            'uint32_t',
            'int32_t',
            'uint64_t',
            'int64_t',
            'float',
            'double',
            'long double'
        ]
        for buffer_type in self.buffer_types:
            if buffer_type not in authorized_types:
                raise ValueError(f"""
                    options.build_types contains an unauthorized type: {buffer_type}
                    Authorized types are: { ", ".join(authorized_types) }
                    """)

    def indent_cpp_spaces(self):
        space = "\t" if self.indent_cpp_with_tabs else " "
        return space * self.indent_cpp_size


def code_style_immvision() -> CodeStyleOptions:
    import internal.code_replacements as _code_replacements

    options = CodeStyleOptions()
    options.generate_to_string = True
    options.indent_cpp_size = 4
    options.srcml_options.functions_api_prefixes = ["IMMVISION_API"]
    options.code_replacements = _code_replacements.standard_replacements() + _code_replacements.opencv_replacements()

    options.buffer_flag_replace_by_array = False

    def init_function_python_additional_code_require_opengl_initialized(function_infos) -> str: # function_infos of type FunctionInfos
        # make sure to transfer the ImGui context before doing anything related to ImGui or OpenGL
        title = function_infos.function_code.docstring_cpp
        if "opengl" in title.lower() and "initialized" in title.lower():
            return "\n    _cpp_immvision.transfer_imgui_context_python_to_cpp()\n\n"
        else:
            return ""

    options.poub_init_function_python_additional_code = init_function_python_additional_code_require_opengl_initialized

    return options


def code_style_implot():
    from litgen.internal import code_replacements

    options = CodeStyleOptions()
    options.generate_to_string = False
    options.indent_cpp_size = 4
    options.srcml_options.functions_api_prefixes = ["IMPLOT_API", "IMPLOT_TMP"]
    options.code_replacements = code_replacements.standard_replacements()

    options.buffer_flag_replace_by_array = True

    options.function_name_exclude_regexes = [
        ####################################################
        #  Legitimate Excludes                             #
        ####################################################

        # Exclude functions whose name end with G, like for example
        #       IMPLOT_API void PlotLineG(const char* label_id, ImPlotGetter getter, void* data, int count);
        # which are made for specialized C/C++ getters
        r"\w*G\Z",
        # Exclude function whose name ends with V, like for example
        #       IMPLOT_API void TagXV(double x, const ImVec4& color, const char* fmt, va_list args) IM_FMTLIST(3);
        # which are utilities for variadic print format
        r"\w*V\Z",


        ####################################################
        #  Excludes due to two dimensional buffer          #
        ####################################################

        #  PlotHeatmap(.., const T* values, int rows, int cols, !!!
        #                            ^          ^          ^
        "PlotHeatmap",


        ####################################################
        #  Excludes due to antique style string vectors    #
        #  for which there is no generalizable parse       #
        ####################################################

        # void SetupAxisTicks(ImAxis idx, const double* values, int n_ticks, const char* const labels[], bool show_default)
        #                                                            ^                           ^
        "SetupAxisTicks",
        # void PlotBarGroupsH(const char* const label_ids[], const T* values, int item_count, int group_count, double group_height=0.67, double y0=0, ImPlotBarGroupsFlags flags=ImPlotBarGroupsFlags_None);
        # void PlotBarGroups (const char* const label_ids[], const T* values, int item_count, int group_count, double group_width=0.67, double x0=0, ImPlotBarGroupsFlags flags=ImPlotBarGroupsFlags_None);
        #                                            ^                                ^
        "PlotBarGroups",
        "PlotBarGroupsH",

        # void PlotPieChart(const char* const label_ids[], const T* values, int count, double x, double y, double radius, bool normalize=false, const char* label_fmt="%.1f", double angle0=90);
        #                                         ^                               ^
        "PlotPieChart"
    ]

    options.srcml_options.code_preprocess_function = _preprocess_imgui_code

    return options


def code_style_imgui():
    options = code_style_implot()
    options.buffer_types += ["float"]
    options.srcml_options.header_guard_suffixes.append("IMGUI_DISABLE")
    return options
