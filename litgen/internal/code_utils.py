import os.path
import re
from typing import List, Tuple, Optional
from code_types import *
from dataclasses import dataclass
import itertools
import logging
import string
import difflib
from pprint import pprint
import traceback


# Identifiers must begin with a letter or an underscore (_)
VALID_IDENTIFIERS_CHARS_START = string.ascii_lowercase + string.ascii_uppercase + "_"
# Then, they can contain letters, digits and underscores
VALID_IDENTIFIERS_CHARS = VALID_IDENTIFIERS_CHARS_START + string.digits
CPP_OPERATORS = list(map(lambda s: "operator" + s,
    "+ - * / % ^ & | ~ ! = < > += -= *= /= %= ^= &= |= << >> >>= <<= == != <= >= <=> && || ++ -- , ->* -> () []"
    .split(" ")
    ))

# transform a list into a list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c]]
def overlapping_pairs(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b


def strip_empty_lines_in_list(code_lines: List[str]) -> List[str]:
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip())  == 0, code_lines))
    code_lines = list(reversed(code_lines))
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip())  == 0, code_lines))
    code_lines = list(reversed(code_lines))

    return code_lines


def strip_empty_lines(code_lines: str) -> str:
    lines = code_lines.split("\n")
    lines = strip_empty_lines_in_list(lines)
    return "\n".join(lines)


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def to_camel_case(name):
    r = ''.join(word.title() for word in name.split('_'))
    return r


def read_text_file(filename: str) -> str:
    with open(filename, "r") as f:
        txt = f.read()
    return txt


def escape_new_lines(code: str) -> str:
    return code.replace("\n", "\\n").replace('"', '\\"')


def write_text_file(filename: str, content: str):
    old_content = read_text_file(filename)
    if content != old_content:
        with open(filename, "w") as f:
            f.write(content)


def unindent_code(code: str) -> str:
    "unindent the code but keep the inner identation"
    indent_size = compute_code_indent_size(code)
    what_to_replace = " " * indent_size

    lines = code.split("\n")

    processed_lines = []
    for line in lines:
        if line.startswith(what_to_replace):
            processed_line = line[indent_size:]
        else:
            processed_line = line
        processed_lines.append(remove_trailing_spaces(processed_line))
    return "\n".join(processed_lines)


def reindent_code(code: str, indent_size: int, skip_first_line = False):
    "change the global code indentation, but keep its inner indentation"
    code = unindent_code(code)
    code = indent_code(code, indent_size, skip_first_line)
    return code


def indent_code(code: str, indent_size: int, skip_first_line = False):
    "add some space to the left of all lines"
    if skip_first_line:
        lines = code.split("\n")
        first_line = lines[0]
        rest = "\n".join(lines[1:])
        return first_line + "\n" + indent_code(rest, indent_size, False)

    lines = code.split("\n")
    indent_str = " " * indent_size
    def indent_line(line):
        if len(line) == 0:
            return ""
        else:
            return indent_str + line
    lines = map(indent_line, lines)
    return "\n".join(lines)


def indent_code_force(code: str, indent_size: int):
    "violently remove all space at the left, thus removign the inner indentation"
    lines = code.split("\n")
    indent_str = " " * indent_size
    lines = map(lambda s: indent_str + s.strip(), lines)
    return "\n".join(lines)


def format_python_comment(comment: str, indent_size: int) -> str:
    lines = comment.split("\n")
    indent_str = " " * indent_size + "# "
    def indent_and_comment_line(line):
        return indent_str + line
    lines = map(indent_and_comment_line, lines)
    return "\n".join(lines)


def format_cpp_comment_on_one_line(comment: str) -> str:
    comment = comment.replace("\n", "\\n")
    comment = comment.replace('"', '\\"')
    return comment


def format_cpp_comment_multiline(comment: str, indentation: int):
    lines = comment.split("\n")
    spacing = " " * indentation
    def process_line(line):
        return spacing + "// " + line
    lines = list(map(process_line, lines))
    return "\n".join(lines)


def write_code_between_markers(
        inout_filename: str,
        code_marker_in: str,
        code_marker_out: str,
        code_to_insert: str,
        flag_preserve_left_spaces: bool
    ):
    assert os.path.isfile(inout_filename)
    input_code = read_text_file(inout_filename)
    input_code_lines = input_code.split("\n")

    output_code = ""
    is_inside_autogen_region = False
    was_replacement_performed = False
    for code_line in input_code_lines:
        if code_marker_in in code_line:
            if is_inside_autogen_region:
                raise RuntimeError(f"Encountered more than one code_marker: {code_marker_in}")
            else:
                is_inside_autogen_region = True
                was_replacement_performed = True
                indent_size = 0
                while indent_size < len(code_line) and code_line[indent_size] == " ":
                    indent_size += 1
                output_code = output_code + code_line + "\n"
                output_code = output_code + "\n"
                if flag_preserve_left_spaces:
                    output_code = output_code + code_to_insert
                else:
                    output_code = output_code + indent_code_force(code_to_insert, indent_size)
        else:
            if not is_inside_autogen_region:
                output_code = output_code + code_line + "\n"
            else:
                pass # Skip code lines that were already in the autogenerated region
        if code_marker_out in code_line:
            output_code = output_code + "\n"
            output_code = output_code + code_line + "\n"
            is_inside_autogen_region = False
    if output_code[-1:] == "\n":
        output_code = output_code[:-1]

    if not was_replacement_performed:
        raise RuntimeError(f"write_code_between_markers: could not find marker {code_marker_in} in file {inout_filename}")

    write_text_file(inout_filename, output_code)


def remove_redundant_spaces(code: str) -> str:
    result = code.strip()
    result = result.replace("\n", " ")
    result = result.replace("\t", " ")

    while True:
        aux = result.replace("  ", " ")
        if aux == result:
            break
        result = aux

    separators = [",", "(", ")", "[", "]", ",", ";"]

    for separator in separators:
        result = result.replace(separator + " ", separator)
        result = result.replace(" " + separator, separator)

    return result


def count_spaces_at_start_of_line(line: str):
    nb_spaces_this_line = 0
    for char in line:
        if char == " ":
            nb_spaces_this_line += 1
        else:
            return nb_spaces_this_line


def compute_code_indent_size(code: str) -> int:
    lines = code.split("\n")
    for line in lines:
        if len(line.replace(" ", "")) == 0:
            continue
        return count_spaces_at_start_of_line(line)
    return 0


def remove_trailing_spaces(line: str) -> str:
    r = line
    while r[-1:] == " ":
        r = r[:-1]
    return r


def make_nice_code_diff(generated: str, expected: str) -> str:
    differ = difflib.Differ()
    diffs = list(differ.compare(expected.splitlines(keepends=True) , generated.splitlines(keepends=True)))
    return "".join(diffs)


def assert_are_equal_ignore_spaces(generated_code: str, expected_code: str):
    generated_processed = remove_redundant_spaces(str(generated_code))
    expected_processed = remove_redundant_spaces(expected_code)
    if not generated_processed == expected_processed:
        diff_str = make_nice_code_diff(generated_processed, expected_processed)
        logging.error(f"""assert_force_one_space_equal returns false 
                    with diff= 
{str(diff_str)}
                    expected_processed=
{expected_processed}
                    and generated_processed=
{generated_processed}
        """)

        stack_lines = traceback.format_stack()
        error_line = stack_lines[-2]
        logging.error(error_line.strip())

    assert generated_processed == expected_processed


def assert_are_codes_equal(generated_code: str, expected_code: str) -> str:
    generated_processed = strip_empty_lines(unindent_code(generated_code))
    expected_processed = strip_empty_lines(unindent_code(expected_code))
    if not generated_processed == expected_processed:
        diff_str = make_nice_code_diff(generated_processed, expected_processed)
        logging.error(f"""assert_are_codes_equal returns false 
                    with diff= 
{str(diff_str)}
                    expected_processed=
{expected_processed}
                    and generated_processed=
{generated_processed}
        """)

        stack_lines = traceback.format_stack()
        error_line = stack_lines[-2]
        logging.error(error_line.strip())

    assert generated_processed == expected_processed


def remove_end_of_line_cpp_comments(code: str) -> str:
    lines = code.split("\n")

    def remove_comment(line: str):
        if "//" in line:
            line = line[ : line.index("//")]
        return line

    lines = map(remove_comment, lines)
    code = "\n".join(lines)
    return code



def is_correct_c_identifier(name: str) -> bool:
    """
    The general rules for naming variables are:
        Names can contain letters, digits and underscores
        Names must begin with a letter or an underscore (_)
        Names are case sensitive (myVar and myvar are different variables)
        Names cannot contain whitespaces or special characters like !, #, %, etc.
        Reserved words (like C++ keywords, such as int) cannot be used as names
    """
    if len(name) == 0:
        return False
    if name[0] not in VALID_IDENTIFIERS_CHARS_START:
        return False
    for c in name[1:]:
        if c not in VALID_IDENTIFIERS_CHARS:
            return False
    return True


def reserved_cpp_keywords():
    keywords_str = (
            "alignas alignof and and_eq asm atomic_cancel atomic_commit atomic_noexcept auto bitand bitor bool break case catch char "
            + "char8_t  char16_t char32_t class compl concept  const consteval  constexpr constinit  const_cast continue co_await "
            + "co_return  co_yield  decltype default delete do double dynamic_cast else enum explicit export extern false float "
            + "for friend goto if inline int long mutable namespace new noexcept not not_eq nullptr operator or or_eq private protected "
            + "public reflexpr register  reinterpret_cast requires  return short signed sizeof static static_assert static_cast struct "
            + "switch synchronized template this thread_local throw true try typedef typeid typename union unsigned using virtual void "
            + "volatile wchar_t while xor xor_eq" )

    keywords = keywords_str.split(" ")
    return keywords


def parse_c_identifier_at_start(code: str) -> Tuple[str, int]:
    if len(code) == 0:
        raise ValueError("parse_c_identifier_at_start cannot accept empty strings")
    if code[0] not in VALID_IDENTIFIERS_CHARS_START:
        return "", -1

    pos = 1
    while pos < len(code):
        if code[pos] not in VALID_IDENTIFIERS_CHARS:
            break
        pos = pos + 1

    identifer = code[:pos]

    if identifer in reserved_cpp_keywords():
        raise ValueError("parse_c_identifier_at_start cannot return a reserved keyword")

    return identifer, pos


def parse_c_identifier_at_end(code: str) -> Tuple[str, int]:
    if len(code) == 0:
        raise CppParseException("parse_c_identifier_at_start cannot accept empty strings")
    if code[-1] not in VALID_IDENTIFIERS_CHARS:
        return "", -1

    pos = len(code) - 1
    while pos >= 0:
        c = code[pos]
        if c not in VALID_IDENTIFIERS_CHARS:
            break
        pos = pos - 1

    pos = pos +  1
    identifer = code[pos:]
    if identifer[0] not in VALID_IDENTIFIERS_CHARS_START:
        return "", -1

    if identifer in reserved_cpp_keywords():
        raise CppParseException("parse_c_identifier_at_start cannot return a reserved keyword")

    return identifer, pos


@dataclass
class FunctionNameAndReturnType:
    name_cpp: str = ""
    return_type_cpp: str = ""
    is_static: bool = False


def remove_template_from_return_type(type_str: str) -> str:
    if not type_str.startswith("template"):
        return type_str

    type_str = type_str.replace("template", "").strip()

    if type_str[0] == "<":
        pos = 1
        nb_chevrons = 1
        while pos < len(type_str) and nb_chevrons > 0:
            char = type_str[pos]
            if char == "<":
                nb_chevrons += 1
            if char == ">":
                nb_chevrons -= 1
            if nb_chevrons == 0:
                break
            pos += 1
        assert nb_chevrons == 0

        type_str = type_str[pos + 1 : ].strip()

    return type_str


def remove_template_and_inline_from_return_type(type_str: str) -> str:
    type_str = remove_template_from_return_type(type_str)
    if type_str.startswith("inline"):
        type_str = type_str.replace("inline", "").strip()
    type_str = remove_template_from_return_type(type_str)

    return type_str


def parse_function_declaration(code_line: str) -> Optional[FunctionNameAndReturnType]:
    if "(" not in code_line:
        return None

    def find_first_paren_in_main_scope(pos_start: int) -> int:
        nb_chevrons = 0
        nb_accolades = 0
        nb_equal = 0
        for pos, char in enumerate(code_line[pos_start :]):
            if char == "=":
                nb_equal += 1
            if char == "<":
                nb_chevrons += 1
            if char == ">":
                nb_chevrons -= 1
            if char == "{":
                nb_accolades += 1
            if char == "}":
                nb_accolades -= 1
            if char == "(" and nb_chevrons == 0 and nb_accolades == 0 and nb_equal == 0:
                return pos + pos_start
        return -1

    pos_first_paren = find_first_paren_in_main_scope(0)

    # special case for operator()
    if (pos_first_paren > len("operator(") and
            code_line[ pos_first_paren - len("operator") : pos_first_paren + 2] == "operator()"):
        pos_first_paren = find_first_paren_in_main_scope(pos_first_paren + 2)

    if pos_first_paren < 0:
        return None

    return_type_and_function_name = code_line[0 : pos_first_paren].strip()

    idx_start_fn_identifier = -1
    for op in CPP_OPERATORS:
        if return_type_and_function_name.endswith(op):
            function_name = op
            idx_start_fn_identifier = return_type_and_function_name.index(op)

    if idx_start_fn_identifier < 0:
        function_name, idx_start_fn_identifier  = parse_c_identifier_at_end(return_type_and_function_name)

    # Special case for destructors
    if idx_start_fn_identifier > 0 and return_type_and_function_name[idx_start_fn_identifier - 1] =="~":
        function_name = "~" + function_name
        return_type_cpp = ""
        return FunctionNameAndReturnType(function_name, return_type_cpp)

    if len(function_name) == 0:
        raise CppParseException(f"parse_function_declaration; empty function name!")
    function_name = function_name.strip()

    return_type_cpp = return_type_and_function_name[ : idx_start_fn_identifier].strip()

    return_type_cpp = remove_template_and_inline_from_return_type(return_type_cpp)

    is_static = False
    if contains_word(return_type_cpp, "static"):
        return_type_cpp = return_type_cpp.replace("static", "").strip()
        is_static = True

    return FunctionNameAndReturnType(function_name, return_type_cpp, is_static=is_static)


def contains_word(where_to_search: str, word: str):
    word = word.replace("*", "\\*")
    regex_str = r"\b" + word + r"\b"
    return does_match_regex(regex_str, where_to_search)


def contains_word_boundary_left_only(where_to_search: str, word: str):
    word = word.replace("*", "\\*")
    regex_str = r"\b" + word
    return does_match_regex(regex_str, where_to_search)


def contains_pointer_type(full_type_str: str, type_to_search: str):
    if type_to_search.endswith("*"):
        type_to_search = type_to_search[:-1]

    if contains_word_boundary_left_only(full_type_str, type_to_search +  "*"):
        return True

    if contains_word_boundary_left_only(full_type_str, type_to_search +  " *"):
        return True

    return False


def does_match_regex(regex_str: str, word: str) -> bool:
    matches = list(re.finditer(regex_str, word, re.MULTILINE))
    return len(matches) > 0


def does_match_regexes(regex_strs: List[str], word: str) -> bool:
    for regex_str in regex_strs:
        if does_match_regex(regex_str, word):
            return True


def make_regex_any_variable_ending_with(what_to_find: str) -> str:
    # For example, this matches only variable
    # ending with count or Count:
    #               r"\b[A-Za-z0-9_]*[Cc]ount\b"

    regex_template = r"\b[A-Za-z0-9_]*WHAT_REGEX\b"
    what_regex = f"[{what_to_find[0].lower()}{what_to_find[0].upper()}]{what_to_find[1:].lower()}"
    regex = regex_template.replace("WHAT_REGEX", what_regex)
    return regex


def make_regex_any_variable_starting_with(what_to_find: str) -> str:
    regex_template = r"\bWHAT_REGEX[A-Za-z0-9_]*\b"
    what_regex = f"[{what_to_find[0].lower()}{what_to_find[0].upper()}]{what_to_find[1:].lower()}"
    regex = regex_template.replace("WHAT_REGEX", what_regex)
    return regex
