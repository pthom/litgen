"""
## Struct and Enum members title policy

    Two policies are possible:

    Policy 1, if members_title_on_previous_line==False:

            ````cpp
            // Plot style structure         <=== this is the struct title. It *has to be on top, and can span several lines
            // Another line in the title
            struct ImPlotStyle {
                // item styling variables   <=== this is the beginning of a code region, with this title
                float   LineWeight;              // = 1, item line weight  <=== member title begins after //
                int     Marker;                  // = ImPlotMarker_None, marker specification
                // plot styling variables   <=== this is the beginning of a code region, with this title
                float   PlotBorderSize;          // = 1,      line thickness of border around plot area
            ````

    Policy 2, if members_title_on_previous_line==True:

            ````cpp
            // Set of display parameters and options for an Image <=== this is the struct title. It *has to be on top, and can span several lines
            struct ImageParams  // IMMVISION_API_STRUCT           <=== IMMVISION_API_STRUCT is a marker for the parsing, not included in the title
            {
                //                                                <=== this is the beginning of a code region, indicated by an empty comment line
                // ImageParams store the parameters for a displayed image
                // Its values will be updated when the user pans or zooms the image, adds watched pixels, etc.
                //                                                <=== end of the code region title, indicated by an empty comment line


                // Refresh Image: set to true if your image matrix/buffer has changed <== member title
                // (for example, for live video images)
                bool RefreshImage = false;
            ````


## Functions, structs and enums title policy

    For functions, structs and enums, the title is always on the line(s) before.
    For example:

                ````cpp
                // Important info
                // info line 2
                enum MyEnum {
                    MyEnum_Value0 = 0;    // Some doc about this value
                };
                ````
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple, Callable
from internal.code_utils import make_regex_any_variable_ending_with, make_regex_any_variable_starting_with
from internal.srcml.srcml_options import SrcmlOptions


def _preprocess_imgui_code(code):
    import re
    new_code = code
    new_code  = re.sub(r'IM_FMTARGS\(\d\)', '', new_code)
    new_code  = re.sub(r'IM_FMTLIST\(\d\)', '', new_code)
    return new_code


@dataclass
class CodeStyleOptions:
    srcml_options: SrcmlOptions = SrcmlOptions()

    # Enum members title policy: are titles directly on top (True), or to the right (False)
    enum_title_on_previous_line: bool = False

    # Shall we generate a __str__() method for structs
    generate_to_string: bool = False
    # functions to exclude by name
    function_name_exclude_regexes: List[str] = field(default_factory=list)
    # enable to exclude functions by adding a comment on the same line of their declaration
    function_exclude_by_comment: List[str] = field(default_factory=list)
    # Suffixes that denote structs that should be published, for example:
    #       struct MyStruct        // IMMVISION_API_STRUCT     <== this is a suffix
    #       { };
    # if empty, all structs are published
    struct_api_suffixes = []

    # List of code replacements when going from C++ to Python (for example double -> float, vector-> List, etc)
    code_replacements = [] # List[StringReplacement]

    # Function that may generate additional code in the function defined in the  __init__.py file of the package
    init_function_python_additional_code = None # Callable[[FunctionsInfos], str]

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
    enum_flag_remove_values_prefix: bool = True
    # Skip count value from enums, for example like in:
    #    enum MyEnum { MyEnum_A = 1, MyEnum_B = 1, MyEnum_COUNT };
    enum_flag_skip_count: bool = True

    # Typed accessor
    def get_code_replacements(self):
        return self.code_replacements

    #
    # Python package names:
    #
    # Name of the native package
    package_name_native: str = "undefined_package_name_native"
    # Name of an optional python wrapper package that calls the native functions
    package_name_python_wrapper: str = "undefined_package_name_python_wrapper"

    #
    # C Buffers to py::array
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
    options.enum_title_on_previous_line = True
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

    options.init_function_python_additional_code = init_function_python_additional_code_require_opengl_initialized

    options.package_name_native = "_cpp_immvision"
    options.package_name_python_wrapper = "immvision"

    return options


def code_style_implot():
    import internal.code_replacements as _code_replacements

    options = CodeStyleOptions()
    options.enum_title_on_previous_line = False
    options.generate_to_string = False
    options.indent_cpp_size = 4
    options.srcml_options.functions_api_prefixes = ["IMPLOT_API", "IMPLOT_TMP"]
    options.code_replacements = _code_replacements.standard_replacements()

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
    options.srcml_options.header_guard_suffixes.append("IMGUI_DISABLE")
    return options
