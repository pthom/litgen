from __future__ import annotations
import difflib
import itertools
import logging
import os.path
import pathlib
import re
import traceback
from typing import Any, Optional, TypeVar
from collections.abc import Iterable, Iterator


"""Low level code utilities

Note: This module shall work standalone, and not depend on anything inside litgen or srcmlcpp!
"""

T = TypeVar("T")


# transform a list into a list of adjacent pairs
# For example : [a, b, c] -> [ [a, b], [b, c]]
def overlapping_pairs(iterable: Iterable[T]) -> Iterator[tuple[T, T]]:
    it = iter(iterable)

    a = next(it, None)
    if a is not None:
        for b in it:
            yield a, b
            a = b


def run_length_encode(in_list: list[T]) -> list[tuple[T, int]]:
    if in_list is None or len(in_list) == 0:
        return []

    out_list = [(in_list[0], 1)]

    for item in in_list[1:]:
        # If same as last, up count, otherwise new element with count 1.
        if item == out_list[-1][0]:
            out_list[-1] = (item, out_list[-1][1] + 1)  # type: ignore
        else:
            out_list.append((item, 1))

    return out_list  # type: ignore


def str_or_none_token(s: Optional[str]) -> str:
    if s is None:
        return "__NONE__"
    else:
        return s


def str_none_empty(s: Optional[str]) -> str:
    if s is None:
        return ""
    else:
        return s


def strip_empty_lines_in_list(code_lines: list[str]) -> list[str]:
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip()) == 0, code_lines))
    code_lines = list(reversed(code_lines))
    code_lines = list(itertools.dropwhile(lambda s: len(s.strip()) == 0, code_lines))
    code_lines = list(reversed(code_lines))

    return code_lines


def code_set_max_consecutive_empty_lines(code: str, nb_max_empty: int) -> str:
    if nb_max_empty < 0:
        return code

    lines = code.split("\n")
    rle: list[tuple[str, int]] = run_length_encode(lines)

    new_lines = []
    for line, nb in rle:
        if len(line.strip()) == 0 and nb >= nb_max_empty:  # noqa
            nb = nb_max_empty
        for _ in range(nb):
            new_lines.append(line)
    return "\n".join(new_lines)


def strip_empty_lines(code_lines: str) -> str:
    lines = code_lines.split("\n")
    lines = strip_empty_lines_in_list(lines)
    return "\n".join(lines)


def line_cpp_comment_position(code_line: str) -> Optional[int]:
    in_string = False
    last_char = None
    for i, char in enumerate(code_line):
        if char == '"' and not last_char == "\\":
            in_string = not in_string
        if char == "/" and last_char == "/" and not in_string:
            return i - 1

        last_char = char

    return None


def line_python_comment_position(code_line: str, skip_if_comment_only_line: bool = False) -> Optional[int]:
    """
    Note: parsing comment position in python is complex.
    This method applies naive strategies. May be use the python official parser module?
    Example comments that it can handle:
        a = 5 # my comment
        a = 5 # my "comment"
        a = 5 # my "comment" with # inside
        a = "#" # my comment
        a = '#' # my comment
        a = '''#''' # my comment
    """

    code_line = code_line.replace('"""', '__"')
    code_line = code_line.replace("'''", "__'")
    code_line = code_line.replace("'", '"')

    in_string = False
    has_seen_non_space = False
    for i, char in enumerate(code_line):
        if char == '"':
            in_string = not in_string
        if char == "#" and not in_string:
            if not skip_if_comment_only_line:
                return i
            else:
                if has_seen_non_space:
                    return i

        if not char.isspace():
            has_seen_non_space = True

    return None


def line_python_comment_eol_position(code_line: str) -> Optional[int]:
    return line_python_comment_position(code_line, skip_if_comment_only_line=True)


def align_python_comments_in_block_lines(lines: list[str]) -> list[str]:
    code = "\n".join(lines)
    code2 = align_python_comments_in_block(code)
    out = code2.split("\n")
    return out


def strip_lines_right_space(lines: list[str]) -> list[str]:
    lines_stripped = list(map(lambda line: line.rstrip(), lines))
    return lines_stripped


def align_python_comments_in_block(code: str) -> str:
    lines = code.split("\n")

    comments_positions_or_none = list(map(line_python_comment_eol_position, lines))
    comments_positions: list[int] = list(filter(lambda v: v is not None, comments_positions_or_none))  # type: ignore

    if len(comments_positions) > 0:
        new_lines = []
        max_position: int = max(comments_positions)
        for line in lines:
            comment_position = line_python_comment_eol_position(line)
            if comment_position is not None:
                start = line[:comment_position]
                end = line[comment_position + 1 :]
                nb_spaces = max_position - comment_position
                new_line = start + " " * nb_spaces + "#" + end
                new_lines.append(new_line)
            else:
                new_lines.append(line)
    else:
        return code

    r = "\n".join(new_lines)
    return r


def last_code_position_before_cpp_comment(code_line: str) -> int:
    pos = line_cpp_comment_position(code_line)
    if pos is None:
        return len(code_line.rstrip())

    pos -= 1
    while pos >= 0:
        c = code_line[pos]
        if not c.isspace():
            pos = pos + 1
            break
        pos = pos - 1
    if pos < 0:
        pos = 0
    return pos


def join_lines_with_token_before_cpp_comment(lines: list[str], token: str) -> str:
    if len(lines) == 0:
        return ""

    def add_token_to_line(line):
        pos = last_code_position_before_cpp_comment(line)
        rr = line[:pos] + token + line[pos:]
        return rr

    lines_with_token = list(map(add_token_to_line, lines[:-1])) + [lines[-1]]
    r = "\n".join(lines_with_token)
    return r


def add_item_before_cpp_comment(code: str, item: str) -> str:
    if len(code) == 0:
        return item
    lines = code.split("\n")
    last_line = lines[-1]
    pos = last_code_position_before_cpp_comment(last_line)
    last_line = last_line[:pos] + item + last_line[pos:]
    lines[-1] = last_line
    r = "\n".join(lines)
    return r


def to_snake_case(name: str) -> str:
    if "re1" not in to_snake_case.__dict__:
        to_snake_case.re1 = re.compile("(.)([A-Z][a-z]+)")  # type: ignore
        to_snake_case.re2 = re.compile("__([A-Z])")  # type: ignore
        to_snake_case.re3 = re.compile("([a-z0-9])([A-Z])")  # type: ignore

    name = to_snake_case.re1.sub(r"\1_\2", name)  # type: ignore
    name = to_snake_case.re2.sub(r"_\1", name)  # type: ignore
    name = to_snake_case.re3.sub(r"\1_\2", name)  # type: ignore

    # name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # name = re.sub('__([A-Z])', r'_\1', name)
    # name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def to_camel_case(name: str) -> str:
    r = "".join(word.title() for word in name.split("_"))
    return r


def read_text_file(filename: str) -> str:
    with open(filename, newline="") as f:
        txt = f.read()
    return txt


def escape_new_lines(code: str) -> str:
    return code.replace("\n", "\\n").replace('"', '\\"')


def write_text_file(filename: str, content: str) -> None:
    old_content = read_text_file(filename)
    if content != old_content:
        with open(filename, "w", newline="") as f:
            f.write(content)


def unindent_code(code: str, flag_strip_empty_lines: bool = False) -> str:
    """unindent the code but keep the inner indentation"""
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

    r = "\n".join(processed_lines)

    if flag_strip_empty_lines:
        r = strip_empty_lines(r)

    return r


def reindent_code(code: str, indent_size: int = 4, skip_first_line: bool = False, indent_str: str = "") -> str:
    """change the global code indentation, but keep its inner indentation"""
    code = unindent_code(code)
    code = indent_code(
        code,
        indent_size=indent_size,
        skip_first_line=skip_first_line,
        indent_str=indent_str,
    )
    return code


def indent_code_lines(
    code_lines: list[str],
    indent_size: int = 1,
    skip_first_line: bool = False,
    indent_str: Optional[str] = None,
    rstrip: bool = True,
) -> list[str]:
    code = "\n".join(code_lines)
    r_str = indent_code(code, indent_size, skip_first_line, indent_str)
    r = r_str.split("\n")
    return r


def indent_code(
    code: str,
    indent_size: int = 1,
    skip_first_line: bool = False,
    indent_str: Optional[str] = None,
    rstrip: bool = True,
) -> str:
    """add some space to the left of all lines"""
    if skip_first_line:
        lines = code.split("\n")
        if len(lines) == 1:
            return code
        first_line = lines[0]
        if rstrip:
            first_line = first_line.rstrip()
        rest = "\n".join(lines[1:])
        return first_line + "\n" + indent_code(rest, indent_size, False, indent_str, rstrip)

    lines = code.split("\n")
    if indent_str is None:
        indent_str_value = " " * indent_size
    else:
        indent_str_value = indent_str

    def indent_line(line: str) -> str:
        if len(line) == 0:
            return ""
        else:
            if rstrip:
                return indent_str_value + line.rstrip()
            else:
                return indent_str_value + line

    lines = list(map(indent_line, lines))
    return "\n".join(lines)


def indent_code_force(code: str, indent_size: int = 1, indent_str: str = "") -> str:
    """violently remove all space at the left, thus removing the inner indentation"""
    lines = code.split("\n")
    if len(indent_str) == 0:
        indent_str = " " * indent_size

    def do_indent(s: str) -> str:
        return indent_str + s.strip()

    lines = list(map(do_indent, lines))
    return "\n".join(lines)


def format_python_comment(comment: str, indent_size: int) -> str:
    lines = comment.split("\n")
    indent_str = " " * indent_size + "# "

    def indent_and_comment_line(line):
        return indent_str + line

    lines = list(map(indent_and_comment_line, lines))
    return "\n".join(lines)


def escape_backslash_in_comments(comment: str) -> str:
    if len(comment) <= 1:
        return comment
    r = ""

    for c1, c2 in overlapping_pairs(comment):
        if c1 == "\\" and c2 not in ["n", "t", "o", "x", '"', "'"]:
            r += "\\\\"
        else:
            r += c1

    last_char = comment[-1]
    if last_char == "\\":
        r += "\\\\"
    else:
        r += last_char

    return r


def format_cpp_comment_on_one_line(comment: Optional[str]) -> str:
    if comment is None:
        return ""
    is_multiline = "\n" in comment
    comment = comment.replace("\n", "\\n")
    comment = comment.replace('"', '\\"')
    comment = escape_backslash_in_comments(comment)
    if not is_multiline:
        comment = comment.strip()
    return comment


def format_cpp_comment_multiline(comment: str, indentation_size: int = 4, indentation_str: str = "") -> str:
    lines = comment.split("\n")
    if len(indentation_str) == 0:
        indentation_str = " " * indentation_size

    def process_line(line):
        return indentation_str + "// " + line

    lines = list(map(process_line, lines))
    return "\n".join(lines)


def cpp_comment_remove_comment_markers(comment: str) -> str:
    if comment.startswith("//"):
        result = comment[2:].strip()
        return result
    else:
        result = comment
        if result.startswith("/*"):
            result = result[2:].strip()
            if result.endswith("*/"):
                result = result[:-2]
        return result


def spaces_or_tabs_at_line_start(line: str) -> str:
    r = ""
    for c in line:
        if c == " " or c == "\t":
            r += c
        else:
            break
    return r


def write_generated_code_between_markers(
    inout_filename: str,
    marker_token: str,
    code_to_insert: str,
    flag_preserve_indentation: bool = True,
) -> None:
    code_marker_in = f"<{marker_token}>"
    code_marker_out = f"</{marker_token}>"

    if not os.path.isfile(inout_filename):
        raise FileNotFoundError(inout_filename)

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

                indent_str = spaces_or_tabs_at_line_start(code_line)

                output_code = output_code + code_line + "\n"

                if flag_preserve_indentation:
                    code_to_insert = indent_code(code_to_insert, indent_str=indent_str)

                output_code = output_code + code_to_insert

        else:
            if not is_inside_autogen_region:
                output_code = output_code + code_line + "\n"
            else:
                pass  # Skip code lines that were already in the autogenerated region
        if code_marker_out in code_line:
            output_code = output_code + "\n"
            output_code = output_code + code_line + "\n"
            is_inside_autogen_region = False
    if output_code[-1:] == "\n":
        output_code = output_code[:-1]

    if not was_replacement_performed:
        is_python_file = inout_filename.endswith("py")
        __ = "#" if is_python_file else "//"
        msg = unindent_code(
            f"""
            Missing marker in {inout_filename} (while calling write_generated_code_between_markers())

            Please write this in your code file {inout_filename} (this section will then be filled automatically):

            {__} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            {__} {code_marker_in}  // Autogenerated code below! Do not edit!
            {__} {code_marker_out} // Autogenerated code end
            {__} !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  AUTOGENERATED CODE END !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """
        )
        raise RuntimeError(msg)
    if output_code != input_code:
        write_text_file(inout_filename, output_code)


def force_one_space(code: str) -> str:
    result = code.strip()
    result = result.replace("\n", " ")
    result = result.replace("\t", " ")
    while True:
        aux = result.replace("  ", " ")
        if aux == result:
            break
        result = aux
    return result


def remove_redundant_spaces(code: str) -> str:
    result = force_one_space(code)
    separators = [",", "(", ")", "[", "]", ",", ";"]

    for separator in separators:
        result = result.replace(separator + " ", separator)
        result = result.replace(" " + separator, separator)

    return result


def count_spaces_at_start_of_line(line: str) -> int:
    nb_spaces_this_line = 0
    for char in line:
        if char == " ":
            nb_spaces_this_line += 1
        else:
            return nb_spaces_this_line
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
    diffs = list(differ.compare(expected.splitlines(keepends=True), generated.splitlines(keepends=True)))
    return "".join(diffs)


def assert_are_equal_ignore_spaces(generated_code: Any, expected_code: str) -> None:
    generated_processed = remove_redundant_spaces(str(generated_code))
    expected_processed = remove_redundant_spaces(expected_code)
    if not generated_processed == expected_processed:
        diff_str = make_nice_code_diff(generated_processed, expected_processed)
        logging.error(
            f"""assert_are_equal_ignore_spaces returns false

                    ========================
                    with diff=
                    ========================
{str(diff_str)}

                    ========================
                    expected_processed=
                    ========================
{expected_processed}

                    ========================
                    and generated_processed=
                    ========================
{generated_processed}
        """
        )

        stack_lines = traceback.format_stack()
        error_line = stack_lines[-2]
        logging.error(error_line.strip())

    assert generated_processed == expected_processed


def assert_are_codes_equal(generated_code: Any, expected_code: str) -> None:
    generated_code_str = str(generated_code)
    generated_processed = strip_empty_lines(unindent_code(generated_code_str))
    expected_processed = strip_empty_lines(unindent_code(expected_code))
    if not generated_processed == expected_processed:
        diff_str = make_nice_code_diff(generated_processed, expected_processed)
        logging.error(
            f"""assert_are_codes_equal returns false
                    ========================
                    with diff=
                    ========================
{str(diff_str)}

                    ========================
                    expected_processed=
                    ========================
{expected_processed}

                    ========================
                    and generated_processed=
                    ========================
{generated_processed}
        """
        )

        stack_lines = traceback.format_stack()
        error_line = stack_lines[-2]
        logging.error(error_line.strip())

    assert generated_processed == expected_processed


def remove_end_of_line_cpp_comments(code: str) -> str:
    lines = code.split("\n")

    def remove_comment(line: str) -> str:
        if "//" in line:
            line = line[: line.index("//")]
        return line

    lines = list(map(remove_comment, lines))
    code = "\n".join(lines)
    return code


def join_remove_empty(separator: str, strs: list[str]) -> str:
    non_empty_strs = filter(lambda s: len(s) > 0, strs)
    r = separator.join(non_empty_strs)
    return r


def contains_word(where_to_search: str, word: str) -> bool:
    word = word.replace("*", "\\*")
    regex_str = r"\b" + word + r"\b"
    return does_match_regex(regex_str, where_to_search)


def contains_word_boundary_left_only(where_to_search: str, word: str) -> bool:
    word = word.replace("*", "\\*")
    regex_str = r"\b" + word
    return does_match_regex(regex_str, where_to_search)


def replace_identifier(cpp_code: str, old_identifier: str, new_identifier: str) -> str:
    # Regular expression pattern for a valid C++ identifier
    pattern = r"\b" + re.escape(old_identifier) + r"\b"
    # Replace the old identifier with the new one
    return re.sub(pattern, new_identifier, cpp_code)


def contains_identifier(cpp_code: str, identifier: str) -> bool:
    if identifier not in cpp_code:
        # Shortcut to avoid the slow regular expression search
        return False
    # Regular expression pattern for a valid C++ identifier
    pattern = r"\b" + re.escape(identifier) + r"\b"
    # Search for the identifier in the code
    return re.search(pattern, cpp_code) is not None


def var_name_contains_word(var_name: str, word: str) -> bool:
    var_name = to_snake_case(var_name).strip()
    word = word.lower()
    if " " in var_name:
        return False
    parts = var_name.split("_")
    for part in parts:
        if part == word:
            return True
    return False


def contains_pointer_type(full_type_str: str, type_to_search: str) -> bool:
    if type_to_search.endswith("*"):
        type_to_search = type_to_search[:-1]

    if contains_word_boundary_left_only(full_type_str, type_to_search + "*"):
        return True

    if contains_word_boundary_left_only(full_type_str, type_to_search + " *"):
        return True

    return False


def does_match_regex(regex_str: str, word: str) -> bool:
    if regex_str.startswith("|"):
        regex_str = regex_str[1:]
    if len(regex_str) == 0:
        return False
    if word is None:
        return False
    matches = list(re.finditer(regex_str, word, re.MULTILINE))
    return len(matches) > 0


def does_match_regexes(regex_strs: list[str], word: str) -> bool:
    if word is None:
        return False
    for regex_str in regex_strs:
        if does_match_regex(regex_str, word):
            return True
    return False


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


def make_regex_exact_word(which_word: str) -> str:
    regex = rf"^{which_word}$"
    return regex


def make_regex_exclude_word(which_word: str) -> str:
    regex = rf"^((?!{which_word}).)*$"
    return regex


def make_regex_var_name_contains_word(word: str) -> str:
    parts = [
        rf"^{word}$",  # Exactly word, or xxx_word or word_xxx, or wordXxx
        rf"^{word}_",  # nb_....
        rf"_{word}$",  # _which
        rf"^{word}[A-Z][a-z_]",
        rf"{word}[0-9]$",
    ]
    r = join_string_by_pipe_char(parts)
    return r


def split_string_by_pipe_char(s: str) -> list[str]:
    items = s.split("|")
    items = list(filter(lambda s: len(s) > 0, items))  # remove empty items
    return items


def join_string_by_pipe_char(strs: list[str]) -> str:
    return "|".join(strs)


def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    res = {**dict1, **dict2}
    return res


def replace_in_string(input_string: str, replacements: dict[str, str]) -> str:
    r = input_string
    for search, replace in replacements.items():
        full_search = "{" + search + "}"
        r = r.replace(full_search, replace)
    return r


def process_code_template(
    input_string: str,
    replacements: dict[str, str],
    replacements_with_line_removal_if_not_found: Optional[dict[str, Optional[str]]] = None,
    flag_replace_maybe_comma: bool = True,
) -> str:
    if replacements_with_line_removal_if_not_found is None:
        replacements_with_line_removal_if_not_found = {}

    r = input_string
    r = replace_in_string(r, replacements)
    r = replace_in_string_remove_line_if_none(r, replacements_with_line_removal_if_not_found)
    if flag_replace_maybe_comma:
        r = r.replace("{maybe_comma}", ", ")
        if r.endswith(", "):
            r = r[:-2]
        if r.endswith(", );"):
            r = r[:-4] + ");"
        if r.endswith(", )"):
            r = r[:-3] + ")"
    return r


def replace_in_string_remove_line_if_none(input_string: str, replacements: dict[str, Optional[str]]) -> str:
    r = input_string

    for search, replace in replacements.items():
        if replace is None:
            lines = r.split("\n")
            new_lines = []
            for line in lines:
                if "{" + search + "}" not in line:
                    new_lines.append(line)
            r = "\n".join(new_lines)
        else:
            full_search = "{" + search + "}"
            r = r.replace(full_search, replace)

    return r


def replace_maybe_comma(code: str, nb_skipped_final_lines: int = 0) -> str:
    """Replace all occurrences of {maybe_comma} by a ',' if it is not on the last line, else by empty."""
    lines = code.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        if "{maybe_comma}" in line:
            if i == len(lines) - 1 - nb_skipped_final_lines:
                line = line.replace("{maybe_comma}", "")
            else:
                line = line.replace("{maybe_comma}", ",")
        new_lines.append(line)
    r = "\n".join(new_lines)
    return r


def word_after(input_string: str, pos: int) -> str:
    remaining = input_string[pos:]
    r = ""
    for c in remaining:
        if c.isspace():
            break
        r += c
    return r


def find_word_after_token(input_string: str, token: str) -> Optional[str]:
    pos = input_string.find(token)
    if pos < 0:
        return None
    r = word_after(input_string, pos + len(token))
    return r


def filename_with_n_parent_folders(filename: str, n: int) -> str:
    if n < 0:
        return filename
    path = pathlib.Path(filename)
    index_start = len(path.parts) - 1 - n
    if index_start < 0:
        index_start = 0
    r = "/".join(path.parts[index_start:])
    return r


def download_url_content(url: str) -> str:
    import ssl
    import urllib.request

    try:
        # Create an unverified SSL context
        ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(url, context=ssl_context) as response:
            data = response.read()
            r: str = data.decode("utf-8")  # noqa
            return r
    except Exception as e:
        return f"An error occurred: {e}"
