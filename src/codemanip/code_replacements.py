from __future__ import annotations
import re
from re import Pattern


class RegexReplacement:
    replace_what_re: Pattern  # type: ignore
    by_what: str

    def __init__(self, replace_what: str, by_what: str) -> None:
        self.replace_what_re = re.compile(replace_what)
        self.by_what = by_what

    def apply(self, s: str) -> str:
        r, nb = self.replace_what_re.subn(self.by_what, s)
        return r

    @staticmethod
    def from_string(line: str) -> RegexReplacement:
        """
        Parses a string of the form
        cv::Matx33d::eye() -> np.eye(3)
        """
        items = line.split(" -> ")

        replace_what_str = items[0].strip()
        by_what = items[1].strip()
        if by_what == "REMOVE":
            by_what = ""

        return RegexReplacement(replace_what_str, by_what)


class RegexReplacementList:
    replacements: list[RegexReplacement]

    def __init__(self) -> None:
        self.replacements = []

    @staticmethod
    def from_string(lines: str) -> RegexReplacementList:
        lines_vec = lines.split("\n")
        lines_vec = list(lines_vec)
        lines_vec = list(map(lambda s: s.strip(), lines_vec))
        lines_vec = list(filter(lambda s: len(s) > 0, lines_vec))
        replacements = list(map(RegexReplacement.from_string, lines_vec))
        r = RegexReplacementList()
        r.replacements = replacements
        return r

    def apply(self, s: str) -> str:
        previous_s = None
        r = s
        max_iterations = 3
        iteration = 0
        while previous_s != r and iteration < max_iterations:
            previous_s = r
            for replacement in self.replacements:
                r = replacement.apply(r)
            iteration += 1
        return r

    def add_last_regex_replacement(self, replacement: RegexReplacement) -> None:
        self.replacements.append(replacement)

    def add_last_replacement(self, replace_what_regex: str, by_what: str) -> None:
        r = RegexReplacement(replace_what_regex, by_what)
        self.add_last_regex_replacement(r)

    def add_first_regex_replacement(self, replacement: RegexReplacement) -> None:
        self.replacements = [replacement] + self.replacements

    def add_first_replacement(self, replace_what_regex: str, by_what: str) -> None:
        r = RegexReplacement(replace_what_regex, by_what)
        self.add_first_regex_replacement(r)

    def merge_replacements(self, other: RegexReplacementList) -> None:
        self.replacements += other.replacements

    def first_replacement(self) -> RegexReplacement:
        assert len(self.replacements) > 0
        return self.replacements[0]
