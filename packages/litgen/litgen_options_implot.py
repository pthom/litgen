from litgen.options import LitgenOptions
from litgen.litgen_options_imgui import litgen_options_imgui


def litgen_options_implot() -> LitgenOptions:
    options = litgen_options_imgui()
    options.srcml_options.functions_api_prefixes = "IMPLOT_API|IMPLOT_TMP"

    options.fn_force_overload__regexes = ["BeginPlot"]
    options.fn_params_exclude_types__regexes = ["ImPlotFormatter"]

    options.fn_params_buffer_types = [
        # // Scalar data types defined by imgui.h
        # // typedef unsigned int        ImGuiID;// A unique ID used by widgets (typically the result of hashing a stack of string)
        # // typedef signed char         ImS8;   // 8-bit signed integer
        # // typedef unsigned char       ImU8;   // 8-bit unsigned integer
        # // typedef signed short        ImS16;  // 16-bit signed integer
        # // typedef unsigned short      ImU16;  // 16-bit unsigned integer
        # // typedef signed int          ImS32;  // 32-bit signed integer == int
        # // typedef unsigned int        ImU32;  // 32-bit unsigned integer (often used to store packed colors)
        # // typedef signed   long long  ImS64;  // 64-bit signed integer
        # // typedef unsigned long long  ImU64;  // 64-bit unsigned integer
        "uint8_t",
        "int8_t",
        "uint16_t",
        "int16_t",
        "uint32_t",
        "int32_t",
        "uint64_t",  # those correspond to `unsigned long` and `long` on linux 64 bits
        "int64_t",  # and they are not available within imgui.h (i.e the ImUXX types need to be reviewed in imgui)
        "float",
        "double",
        # "long double",  # Note: long double not supported in implot (yet?)
        "long long",
    ]

    options.fn_exclude_by_name__regexes = [
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
        "PlotPieChart",
    ]

    return options
