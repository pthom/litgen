from srcmlcpp.srcml_types import *

from litgen.options import LitgenOptions
from litgen.internal.adapted_types_wip.adapted_types import *
from litgen.internal import cpp_to_python


def _add_stub_element(
    adapted_element: AdaptedElement,
    first_code_line: str,
    options: LitgenOptions,
    body_lines: List[str] = [],
    fn_params_and_return: str = "",
) -> str:
    """Common layout for class, enum, and functions stubs"""

    cpp_element = adapted_element._cpp_element

    location = cpp_to_python.info_original_location_python(cpp_element, options)
    first_line = first_code_line + location

    all_lines_except_first = []
    if len(fn_params_and_return) > 0:
        all_lines_except_first += fn_params_and_return.split("\n")
    all_lines_except_first += cpp_to_python.docstring_lines(cpp_element, options)
    all_lines_except_first += body_lines
    if len(body_lines) == 0:
        all_lines_except_first += ["pass"]

    _i_ = options.indent_python_spaces()

    def indent_line(line: str):
        return _i_ + line

    all_lines_except_first = list(map(indent_line, all_lines_except_first))

    all_lines_except_first = code_utils.align_python_comments_in_block_lines(all_lines_except_first)

    all_lines = [first_line] + all_lines_except_first
    all_lines = code_utils.strip_lines_right_space(all_lines)

    r = "\n".join(all_lines) + "\n"

    return r


def _generate_pyi_enum(adapted_enum: AdaptedEnum, options: LitgenOptions) -> str:
    enum = adapted_enum.cpp_element()
    first_code_line = f"class {adapted_enum.enum_name_python()}(Enum):"

    body_lines: List[str] = []

    previous_enum_element: Optional[CppDecl] = None
    for child in enum.block.block_children:
        if isinstance(child, CppDecl):
            # body_lines += _make_enum_element_decl_lines(enum, child, previous_enum_element, options)
            previous_enum_element = child
        if isinstance(child, CppEmptyLine) and options.python_keep_empty_lines:
            body_lines.append("")
        if isinstance(child, CppComment):
            body_lines += cpp_to_python.python_comment_previous_lines(child, options)
    r = _add_stub_element(enum, first_code_line, options, body_lines)
    return r
