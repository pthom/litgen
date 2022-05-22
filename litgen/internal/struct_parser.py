import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR] + sys.path

from dataclasses import dataclass
import copy

from code_types import *
from options import CodeStyleOptions
import code_region_comment_parser
import code_utils
import find_functions_structs_enums
import function_parser


def _try_parse_struct_declaration(line: str, options: CodeStyleOptions) -> Optional[PydefCode]:
    """
    Accepts lines like
        struct ImPlotContext {
    or
        struct ImPlotContext
        {
    but refuses forward declarations like
        struct ImPlotContext;             // ImPlot context (opaque struct, see implot_internal.h)
    """
    full_line = line

    if "//" in line:
        line = line.split("//")[0].strip()
    line = line.strip()
    if line.startswith("struct"):
        items = line.split(" ")
        struct_name = items[1].replace("{", "").strip()
        if struct_name.endswith(";"):
            return None

        if len(options.struct_api_suffixes) > 0:
            found_suffix = False
            for possible_suffix in options.struct_api_suffixes:
                if possible_suffix in full_line:
                    found_suffix = True
            if not found_suffix:
                return None

        return PydefCode(code_type=CppCodeType.STRUCT, name_cpp=struct_name, declaration_line=full_line)
    else:
        return None


@dataclass
class _ParseScopeObserver:
    _nb_ifdef_zone: int  = 0
    _nb_chevrons: int = 0
    _nb_accolades: int = 0
    _nb_paren: int = 0

    # to be called after the processing of the line
    def parse_line(self, code_line: str):
        if code_line.startswith("#ifdef ") or code_line.startswith("#if "):
            self._nb_ifdef_zone += 1
            return []
        if code_line.startswith("#endif"):
            self._nb_ifdef_zone -= 1
            return []

        self._nb_chevrons += code_line.count("<")
        self._nb_chevrons -= code_line.count(">")
        self._nb_accolades += code_line.count("{")
        self._nb_accolades -= code_line.count("}")
        self._nb_paren += code_line.count("(")
        self._nb_paren -= code_line.count(")")

    def was_scope_ok_on_last_line(self):
        if self._nb_ifdef_zone != 0:
            return False
        return (self._nb_ifdef_zone == 0 and self._nb_paren == 0
                and self._nb_accolades == 0 and self._nb_chevrons == 0)


def _try_parse_struct_member(state : _ParseScopeObserver, line_number: int, code_line: str) -> List[PydefAttribute]:
    """
    Can handle lines like
        ColorAdjustmentsValues ColorAdjustments = ColorAdjustmentsValues();
    or
        std::vector <cv::Point> WatchedPixels; // std::vector<cv::Point> is empty by default
    or
        double xStart, yStart, zStart\t, wStart = 0.1; // Comment

    Refuses methods declarations like
        bool Contains(const ImPlotPoint& p) const
    but accepts initialisations like:
        Rect rect = ImPlotRect();
    """

    state.parse_line(code_line)
    if not state.was_scope_ok_on_last_line():
        return []

    # Skip comments only line
    if code_line.startswith("//") or len(code_line.strip()) <= 2 or code_line.startswith("#"):
        return []
    # Reject methods
    if code_utils.parse_function_declaration(code_line) is not None:
        return []

    single_attr_result = PydefAttribute()

    # extract comment
    if "//" in code_line:
        items = code_line.split("//")
        single_attr_result.docstring_cpp = items[1].strip()
        code_line = items[0]

    # Strip trailing ";"
    single_attr_result.line_number = line_number
    code_line = code_line.strip()
    if code_line[-1] == ";":
        code_line = code_line[:-1]

    # Extract default value
    if "=" in code_line:
        first_equal_pos = code_line.index("=")
        single_attr_result.default_value_cpp = code_line[first_equal_pos + 1:].strip()
        code_line = code_line[:first_equal_pos]


    if " " not in code_line:
        raise RuntimeError(f"can't parse attribute at line {code_line}")

    # Refuse arrays
    if "[" in code_line:
        return []

    # Extract attribute name(s). At this stage, we do not separate them
    # if the line is like:
    #      double x, y = 1.;
    def find_index_attributes_names_start() -> int:
        if ">" in code_line:
            last_closing_chevron = code_line.rindex(">")
            first_space_pos = code_line.index(" ", last_closing_chevron)
            return first_space_pos
        else:
            first_space_pos = code_line.index(" ")
            return first_space_pos

        return 0

    # Separate attribute names by ","
    def extract_line_multiple_attributes() -> List[PydefAttribute]:
        index_attributes_names_start = find_index_attributes_names_start()
        names_concatenated = code_line[index_attributes_names_start:].strip()
        attr_names = names_concatenated.split(",")
        attr_names = list(map(lambda s: s.strip(), attr_names))
        attr_type = code_line[:index_attributes_names_start].strip()
        this_line_attributes = []
        for attr_name in attr_names:
            one_attr = copy.deepcopy(single_attr_result)
            one_attr.type_cpp = attr_type
            one_attr.name_cpp = attr_name
            this_line_attributes.append(one_attr)
        return this_line_attributes

    return extract_line_multiple_attributes()



def _extract_struct_attributes(struct_pydef: PydefCode, options: CodeStyleOptions) -> List[PydefAttribute]:
    """
    *Very* dumb parser, that works with our simple structs
    """
    code = struct_pydef.body_code_cpp
    assert code[0] == "{" and code[-1] == "}"
    code = code[1 : -1]

    code_lines = code.split("\n")
    code_lines = map(lambda s: s.strip(), code_lines)
    numbered_code_lines = list(enumerate(code_lines))

    def add_attribute_comment_on_line_before(attribute: PydefAttribute) -> str:
        # Search for comment beginning with // immediately on top of the attribute
        comment_lines_before_attribute_decl = []
        line_number = attribute.line_number - 1
        while line_number >= 0:
            previous_code_line: str = numbered_code_lines[line_number][1]
            if not previous_code_line.startswith("//"):
                break
            previous_code_line = previous_code_line[2:].strip()
            if len(previous_code_line) == 0:
                break
            comment_lines_before_attribute_decl.append(previous_code_line)
            line_number = line_number - 1
        comment_lines_before_attribute_decl = list(reversed(comment_lines_before_attribute_decl))
        attribute.docstring_cpp = "\n".join(comment_lines_before_attribute_decl)

    state = _ParseScopeObserver()
    all_attributes = []
    for line_number, code_line in numbered_code_lines:
        this_line_attributes = _try_parse_struct_member(state, line_number, code_line)
        if len(this_line_attributes) > 0:
            all_attributes = all_attributes + this_line_attributes

    for attribute in all_attributes:
        add_attribute_comment_on_line_before(attribute)
    return all_attributes


def parse_struct_pydef(pydef_code: PydefCode, options: CodeStyleOptions) -> StructInfos:
    struct_infos = StructInfos()
    struct_infos.struct_code = pydef_code

    def parse_methods():
        assert struct_infos.struct_code.body_code_cpp[0] == "{" and struct_infos.struct_code.body_code_cpp[-1] == "}"
        inner_body_code = struct_infos.struct_code.body_code_cpp[1 : -1]
        options_method = copy.deepcopy(options)
        options_method.functions_api_prefixes = []
        methods = function_parser.parse_all_function_declarations(inner_body_code, options_method)
        return methods

    struct_attributes = _extract_struct_attributes(struct_infos.struct_code, options)
    code_region_comments = code_region_comment_parser.extract_code_region_comments(struct_infos.struct_code, options)

    for m in parse_methods():
        v = Variant_Attribute_Method_CodeRegion()
        v.method_infos = m
        v.line_number = m.function_code.line_start
        struct_infos.attr_and_regions.append(v)
    for sa in struct_attributes:
        v = Variant_Attribute_Method_CodeRegion()
        v.line_number = sa.line_number
        v.attribute = sa
        struct_infos.attr_and_regions.append(v)
    for cr in code_region_comments:
        v = Variant_Attribute_Method_CodeRegion()
        v.line_number = cr.line_number
        v.code_region_comment = cr
        struct_infos.attr_and_regions.append(v)

    struct_infos.attr_and_regions = sorted(struct_infos.attr_and_regions, key=lambda x: x.line_number)
    return struct_infos


def parse_one_struct_testonly(code: str, options: CodeStyleOptions):
    function_pydefs = find_functions_structs_enums.find_functions_struct_or_enums(code, CppCodeType.STRUCT, options)
    assert len(function_pydefs) == 1
    struct_infos = parse_struct_pydef(function_pydefs[0], options)
    return struct_infos
