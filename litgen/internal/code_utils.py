import os.path
import re
from typing import List
import itertools
import logging
import difflib
import traceback


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


def reindent_code(code: str, indent_size: int = 4, skip_first_line = False, indent_str = ""):
    "change the global code indentation, but keep its inner indentation"
    code = unindent_code(code)
    code = indent_code(code, indent_size = indent_size, skip_first_line = skip_first_line,indent_str=indent_str)
    return code


def indent_code(code: str, indent_size: int = 1, skip_first_line = False, indent_str = ""):
    "add some space to the left of all lines"
    if skip_first_line:
        lines = code.split("\n")
        if len(lines) == 1:
            return code
        first_line = lines[0]
        rest = "\n".join(lines[1:])
        return first_line + "\n" + indent_code(rest, indent_size, False, indent_str)

    lines = code.split("\n")
    if len(indent_str) == 0:
        indent_str = " " * indent_size

    def indent_line(line):
        if len(line) == 0:
            return ""
        else:
            return indent_str + line

    lines = map(indent_line, lines)
    return "\n".join(lines)


def indent_code_force(code: str, indent_size: int = 1, indent_str = ""):
    "violently remove all space at the left, thus removign the inner indentation"
    lines = code.split("\n")
    if len(indent_str) == 0:
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


def format_cpp_comment_multiline(comment: str, indentation_size: int = 4, indentation_str = ""):
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


def spaces_or_tabs_at_line_start(line) -> str:
    r = ""
    for i, c in enumerate(line):
        if c == " " or c == "\t":
            r += c
        else:
            break
    return r


def write_code_between_markers(
        inout_filename: str,
        code_marker_in: str,
        code_marker_out: str,
        code_to_insert: str,
        flag_preserve_indentation: bool = True
    ):

    while code_to_insert.endswith("\n\n"):
        code_to_insert = code_to_insert[:-1]
    while code_to_insert.startswith("\n\n"):
        code_to_insert = code_to_insert[1:]

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

                indent_str = spaces_or_tabs_at_line_start(code_line)

                output_code = output_code + code_line + "\n"

                if flag_preserve_indentation:
                    code_to_insert = indent_code(code_to_insert, indent_str=indent_str)

                output_code = output_code + code_to_insert

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
        logging.error(f"""assert_are_equal_ignore_spaces returns false 
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
    generated_code_str = str(generated_code)
    generated_processed = strip_empty_lines(unindent_code(generated_code_str))
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


def join_remove_empty(separator: str, strs: List[str]):
    non_empty_strs = filter(lambda s : len(s) > 0, strs)
    r = separator.join(non_empty_strs)
    return r


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


def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res
