from code_types import *
from options import CodeStyleOptions
import comments_parser
import find_functions_structs_enums


def try_parse_enum_cpp_98_declaration(line: str, code_style_options: CodeStyleOptions) -> Optional[PydefCode]:
    full_line = line
    line = line.strip()
    if line.startswith("enum") and not line.startswith("enum class"):
        items = line.split(" ")
        cpp_name = items[1].replace("{", "").strip()
        return PydefCode(code_type=CppCodeType.ENUM_CPP_98, name_cpp=cpp_name, declaration_line=full_line)
    else:
        return None


def parse_enum_value(line_number: int, code_line: str, enum_name: str) -> Optional[PydefEnumCpp98Value]:
    """
    Can handle lines like
        ImPlotDragToolFlags_NoCursors = 1 << 0, // some comment
    or
        ImPlotCol_MarkerOutline, // some comment
    or
        ImPlotCol_MarkerOutline = 3,
    or
        ImAxis_COUNT        <== this should not count as a value
    """
    code_line = code_line.strip()
    if code_line.startswith("{"):
        code_line = code_line[1:]
    if code_line.endswith("}"):
        code_line = code_line[:-1]
    if len(code_line) == 0 or code_line.startswith("//"):
        return None

    r = PydefEnumCpp98Value()
    # fill line_number
    r.line_number = line_number
    # fill comment
    if "//" in code_line:
        items = code_line.split("//")
        r.comment = items[1].strip()
        code_line = items[0].strip()
    # skip end of line after "=" or ","
    if "=" in code_line:
        items = code_line.split("=")
        code_line = items[0].strip()
    else:
        if code_line.endswith(","):
            code_line = code_line[:-1].strip()
    # fill name
    if code_line.endswith("_COUNT"):
        return None
    r.name_cpp = code_line
    r.name_python = r.name_cpp.replace(enum_name, "")
    if r.name_python == "None":
        r.name_python = "None_"

    return r


def _extract_enum_cpp_98_values(enum_pydefcode: PydefCode) -> List[PydefEnumCpp98Value]:
    """
    *Very* dumb parser, that works with code that looks like

        // Plot styling colors.
        enum ImPlotCol_ {
            // item styling colors
            ImPlotCol_Line_Default = 0,
            ImPlotCol_Line,          // plot line/outline color (defaults to next unused color in current colormap)
            ImPlotCol_Fill,          // plot fill color for bars (defaults to the current line color)
            ImPlotCol_MarkerOutline, // marker outline color (defaults to the current line color)
            ImPlotCol_MarkerFill,    // marker fill color (defaults to the current line color)
            ImPlotCol_ErrorBar,      // error bar color (defaults to ImGuiCol_Text)
            // plot styling colors
            ImPlotCol_FrameBg,       // plot frame background color (defaults to ImGuiCol_FrameBg)
            ImPlotCol_PlotBg,        // plot area background color (defaults to ImGuiCol_WindowBg)
        };
    """
    global LAST_ENUM_VALUE
    LAST_ENUM_VALUE = -1

    code_lines = enum_pydefcode.body_code_cpp.split("\n")
    code_lines = map(lambda s: s.strip(), code_lines)
    numbered_code_lines = list(enumerate(code_lines))

    enum_values = []
    for line_number, code_line in numbered_code_lines:
        v = parse_enum_value(line_number, code_line, enum_pydefcode.name_cpp)
        if v is not None:
            enum_values.append(v)

    return enum_values


def parse_enum_cpp_98_pydef(pydef_code: PydefCode, code_style_options: CodeStyleOptions) -> EnumCpp98Infos:
    r = EnumCpp98Infos()
    r.enum_code = pydef_code
    enum_values = _extract_enum_cpp_98_values(r.enum_code)
    code_region_comments = comments_parser.extract_code_region_comments(r.enum_code, code_style_options)
    for ev in enum_values:
        v = Variant_Attribute_Method_CodeRegion()
        v.line_number = ev.line_number
        v.enum_cpp_98_value = ev
        r.attr_and_regions.append(v)
    for cr in code_region_comments:
        v = Variant_Attribute_Method_CodeRegion()
        v.line_number = cr.line_number
        v.code_region_comment = cr
        r.attr_and_regions.append(v)

    r.attr_and_regions = sorted(r.attr_and_regions, key=lambda x: x.line_number)
    return r


def parse_all_enum_cpp_98(code: str, options: CodeStyleOptions) -> List[EnumCpp98Infos]:
    enums_pydefs = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.ENUM_CPP_98, options)
    enum_infos = list(map(lambda enum_pydef: parse_enum_cpp_98_pydef(enum_pydef, options), enums_pydefs))
    return enum_infos
