import os, sys
_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR)

from code_types import *
from options import CodeStyleOptions
import struct_parser, enum_parser, function_parser
import code_utils

def _fill_pydef_body_code(code_lines: List[str], pydef_type: CppCodeType, pydef_code_inout: PydefCode):
    """Fills the body of a struct, function or enum, given a partially filled PydefCode
    """
    body_lines = []
    lines_under_pydef = code_lines[pydef_code_inout.line_start:]
    flag_entered_body = False
    flag_exited_body = False

    if pydef_type == CppCodeType.STRUCT:
        opening_token = "{"
        closing_token = "}"
    elif pydef_type == CppCodeType.FUNCTION:
        opening_token = "("
        closing_token = ")"
    elif pydef_type == CppCodeType.ENUM_CPP_98:
        opening_token = "{"
        closing_token = "}"
    else:
        raise(f"fill_pydef_body_code: unsupported pydef_type {pydef_type}")

    nb_opening_tokens = 0

    def count_tokens(line):
        return line.count(opening_token) - line.count(closing_token)

    def append_body_line(line):
        if len(line) > 0:
            body_lines.append(line)

    for line_number, code_line in enumerate(lines_under_pydef):
        if flag_exited_body:
            break
        body_line = ""
        for character in code_line:
            nb_opening_tokens += count_tokens(character)
            if not flag_entered_body and nb_opening_tokens == 1:
                flag_entered_body = True
            if flag_entered_body and not flag_exited_body:
                body_line += character
            if nb_opening_tokens == 0 and flag_entered_body:
                flag_exited_body = True
                pydef_code_inout.line_end = line_number + pydef_code_inout.line_start
        append_body_line(body_line)

    body_lines = code_utils.strip_empty_lines_in_list(body_lines)
    result = "\n".join(body_lines)
    pydef_code_inout.body_code_cpp = result


def find_functions_struct_or_enums(
        whole_file_code: str,
        code_type: CppCodeType,
        options: CodeStyleOptions) -> List[PydefCode]:

    function_parser._reset_parse_state()
    fn_try_parse_code_type = None
    if code_type == CppCodeType.STRUCT:
        fn_try_parse_code_type = struct_parser._try_parse_struct_declaration
    if code_type == CppCodeType.ENUM_CPP_98:
        fn_try_parse_code_type = enum_parser.try_parse_enum_cpp_98_declaration
    if code_type == CppCodeType.FUNCTION:
        fn_try_parse_code_type = function_parser.try_parse_function_name_from_declaration
    assert fn_try_parse_code_type is not None

    code_lines = whole_file_code.split("\n")
    pydef_codes = []
    for line_number, code_line in enumerate(code_lines):
        pydef_code = fn_try_parse_code_type(code_line, options)
        if pydef_code is not None:
            pydef_code.title_cpp = _read_comment_on_top_of_line(code_lines, options, line_number)
            pydef_code.line_start = line_number
            pydef_codes.append(pydef_code)

    for pydef_code in pydef_codes:
        _fill_pydef_body_code(code_lines, code_type, pydef_code)
    return pydef_codes


def _read_comment_on_top_of_line(code_lines: List[str], options: CodeStyleOptions, line_nb: int) -> str:
    """Read the comment on top of a function, struct, or enum
    We have this kind of code, where the title is on top
          // Title line 1
          // Title continued on line 2
          struct Foo {          <--- input line_nb
    """
    title_start = line_nb
    while title_start > 1:
        previous_line = code_lines[title_start - 1]
        if previous_line.strip().startswith("//"):
            title_start -= 1
        else:
            break
    line_start = title_start

    title_lines = []
    while line_start < len(code_lines):
        line = code_lines[line_start].strip()
        if not line.startswith("//"):
            break
        title_lines.append(line[2:].strip())
        line_start += 1
    title = "\n".join(title_lines)
    title = title.strip()
    return title
