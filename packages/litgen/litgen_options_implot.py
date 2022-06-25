from litgen.options import LitgenOptions
from litgen.litgen_options_imgui import litgen_options_imgui


def litgen_options_implot() -> LitgenOptions:
    options = litgen_options_imgui()
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
        "PlotPieChart",
    ]

    return options
