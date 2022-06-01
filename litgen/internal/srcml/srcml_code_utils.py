from typing import List


def merge_dicts(dict1, dict2):
    res = {**dict1, **dict2}
    return res


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


def join_remove_empty(separator: str, strs: List[str]):
    non_empty_strs = filter(lambda s : len(s) > 0, strs)
    r = separator.join(non_empty_strs)
    return r
