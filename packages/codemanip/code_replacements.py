import re
from dataclasses import dataclass
from typing import List


@dataclass
class StringReplacement:
    replace_what: str = ""
    by_what: str = ""


def _parse_string_replacement(line: str) -> StringReplacement:
    """
    Parses a string of the form
    cv::Matx33d::eye() -> np.eye(3)
    """
    items = line.split(" -> ")
    r = StringReplacement()
    r.replace_what = items[0].strip()
    r.by_what = items[1].strip()
    if r.by_what == "REMOVE":
        r.by_what = ""
    return r


def parse_string_replacements(lines: str) -> List[StringReplacement]:
    lines_vec = lines.split("\n")
    lines_vec = list(lines_vec)
    lines_vec = list(map(lambda s: s.strip(), lines_vec))
    lines_vec = list(filter(lambda s: len(s) > 0, lines_vec))
    r = list(map(_parse_string_replacement, lines_vec))
    return r


def apply_one_replacement(s: str, replacement: StringReplacement) -> str:
    regex = replacement.replace_what
    subst = replacement.by_what
    r, nb = re.subn(regex, subst, s)
    return r


def apply_code_replacements(s: str, replacements: List[StringReplacement]) -> str:
    r = s
    for replacement in replacements:
        r = apply_one_replacement(r, replacement)
    return r
