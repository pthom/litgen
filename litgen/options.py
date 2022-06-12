from dataclasses import dataclass, field
from typing import List, Dict

from litgen.internal.code_utils import make_regex_any_variable_ending_with, make_regex_any_variable_starting_with
from srcmlcpp import SrcmlOptions


class CodeStyleOptions:
    """Configuration of the code generation (include / excludes, indentation, c++ to python translation settings, etc.)
    """

    #
    # There are interesting options to set in SrcmlOptions (see srcmlcpp/srcml_options.py)
    #
    # Notably:
    # * fill srcml_options.functions_api_prefixes
    #   (the prefixes that denotes the functions that shall be published)
    # * Also, fill the excludes if you encounter issues with some functions or declarations you want to ignore
    srcml_options: SrcmlOptions = SrcmlOptions()

    #
    # Shall the binding show the original location of elements as a comment
    #
    original_location_flag_show = False
    # if showing location, how many parent folders shall be shown
    original_location_nb_parent_folders = 0


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
    indent_python_with_tabs: bool = False
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
    buffer_flag_replace_by_array = True
    buffer_types: List[str] = ["int8_t", "uint8_t"] # of type List[str]. Which means that `uint8_t*` are considered as possible buffers
    buffer_template_types: List[str] = ["T"] # Which means that templated functions using a buffer use T as a templated name
    buffer_size_regexes: List[str] = [
        make_regex_any_variable_ending_with("count"),   # any variable name ending with count or Count
        make_regex_any_variable_starting_with("count"), # any variable name starting with count or Count
        make_regex_any_variable_ending_with("size"),
        make_regex_any_variable_starting_with("size"),
    ]

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

    #
    # C style arrays structs and class members
    #
    # If c_array_numeric_member_flag_replace is active, then members like
    #       struct Foo {  int values[10]; };
    # will be transformed to a property that points to a numpy array
    # which can be read/written from python (this requires numpy)
    c_array_numeric_member_flag_replace = True
    # list of numeric types that can be stored in a numpy array
    c_array_numeric_member_types = [     # don't include char !
        "int",                           # See https://numpy.org/doc/stable/reference/generated/numpy.chararray.html
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
    # List of named possible sizes (fill it if some sizes are defined by macros or constexpr values)
    c_array_numeric_member_size_dict: Dict[str, int] = {}

    # If c_string_list_flag_replace is active, then C string lists `(const char **, size_t)`
    # will be replaced by `const std::vector<std::string>&`. For example:
    #     void foo(const char * const items[], int items_count)
    # will be transformed to:
    #     void foo(const std::vector<std::string>& const items[])
    c_string_list_flag_replace = True

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

    def indent_python_spaces(self):
        space = "\t" if self.indent_python_with_tabs else " "
        return space * self.indent_python_size

    def __init__(self):
        self.srcml_options = SrcmlOptions()


#
# Example of configurations for several libraries (immvision, imgui, implot)
#


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


def _preprocess_imgui_code(code):
    """
    The imgui code uses two macros (IM_FMTARGS and IM_FMTLIST) which help the compiler
        #define IM_FMTARGS(FMT)             __attribute__((format(printf, FMT, FMT+1)))
        #define IM_FMTLIST(FMT)             __attribute__((format(printf, FMT, 0)))

    They are used like this:
        IMGUI_API bool          TreeNode(const char* str_id, const char* fmt, ...) IM_FMTARGS(2);

    They are removed before processing the header, because they would not be correctly interpreted by srcml.
    """
    import re
    new_code = code
    new_code  = re.sub(r'IM_FMTARGS\(\d\)', '', new_code)
    new_code  = re.sub(r'IM_FMTLIST\(\d\)', '', new_code)
    return new_code


def code_style_imgui():
    from litgen.internal import code_replacements

    options = CodeStyleOptions()

    options.generate_to_string = False
    options.indent_cpp_size = 4

    options.code_replacements = code_replacements.standard_replacements()
    options.buffer_flag_replace_by_array = True

    options.srcml_options.functions_api_prefixes = ["IMGUI_API"]
    options.srcml_options.header_guard_suffixes.append("IMGUI_DISABLE")

    options.buffer_types += ["float"]
    options.c_array_numeric_member_types += ["ImGuiID", "ImS8", "ImU8", "ImS16", "ImU16", "ImS32", "ImU32", "ImS64", "ImU64"]

    options.srcml_options.code_preprocess_function = _preprocess_imgui_code

    options.srcml_options.function_name_exclude_regexes = [
        # IMGUI_API void          SetAllocatorFunctions(ImGuiMemAllocFunc alloc_func, ImGuiMemFreeFunc free_func, void* user_data = NULL);
        #                                               ^
        # IMGUI_API void          GetAllocatorFunctions(ImGuiMemAllocFunc* p_alloc_func, ImGuiMemFreeFunc* p_free_func, void** p_user_data);
        #                                               ^
        # IMGUI_API void*         MemAlloc(size_t size);
        #           ^
        # IMGUI_API void          MemFree(void* ptr);
        #                                 ^
        r"\bGetAllocatorFunctions\b",
        r"\bSetAllocatorFunctions\b",
        r"\bMemAlloc\b",
        r"\bMemFree\b",
        # IMGUI_API void              GetTexDataAsAlpha8(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 1 byte per-pixel
        #                                                             ^
        # IMGUI_API void              GetTexDataAsRGBA32(unsigned char** out_pixels, int* out_width, int* out_height, int* out_bytes_per_pixel = NULL);  // 4 bytes-per-pixel
        #                                                             ^
        r"\bGetTexDataAsAlpha8\b",
        r"\bGetTexDataAsRGBA32\b",
        # IMGUI_API ImVec2            CalcTextSizeA(float size, float max_width, float wrap_width, const char* text_begin, const char* text_end = NULL, const char** remaining = NULL) const; // utf8
        #                                                                                                                                                         ^
        r"\bCalcTextSizeA\b"
    ]

    options.srcml_options.decl_name_exclude_regexes = [
        #     typedef void (*ImDrawCallback)(const ImDrawList* parent_list, const ImDrawCmd* cmd);
        #     ImDrawCallback  UserCallback;       // 4-8  // If != NULL, call the function instead of rendering the vertices. clip_rect and texture_id will be set normally.
        #     ^
        r"\bUserCallback\b",
        # struct ImDrawData
        # { ...
        #     ImDrawList**    CmdLists;               // Array of ImDrawList* to render. The ImDrawList are owned by ImGuiContext and only pointed to from here.
        #               ^
        # }
        r"\bCmdLists\b"
    ]

    return options


def code_style_implot():
    options = code_style_imgui()
    options.srcml_options.functions_api_prefixes = ["IMPLOT_API", "IMPLOT_TMP"]

    options.srcml_options.function_name_exclude_regexes = [
        #  Legitimate Excludes

        # Exclude functions whose name end with G, like for example
        #       IMPLOT_API void PlotLineG(const char* label_id, ImPlotGetter getter, void* data, int count);
        # which are made for specialized C/C++ getters
        r"\w*G\Z",
        # Exclude function whose name ends with V, like for example
        #       IMPLOT_API void TagXV(double x, const ImVec4& color, const char* fmt, va_list args) IM_FMTLIST(3);
        # which are utilities for variadic print format
        r"\w*V\Z",


        #  Excludes due to two-dimensional buffer

        #  PlotHeatmap(.., const T* values, int rows, int cols, !!!
        #                            ^          ^          ^
        "PlotHeatmap",


        #  Excludes due to antique style string vectors
        #  for which there is no generalizable parse

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

    return options
