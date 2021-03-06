from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Pattern


class RegexReplacement:
    replace_what_re: Pattern
    by_what: str

    def __init__(self, replace_what: str, by_what: str) -> None:
        self.replace_what_re = re.compile(replace_what)
        self.by_what = by_what

    def apply(self, s: str) -> str:
        # regex = self.replace_what_re
        # subst = self.by_what
        # r, nb = re.subn(regex, subst, s)

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
    replacements: List[RegexReplacement]

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
        r = s
        for replacement in self.replacements:
            r = replacement.apply(r)
        return r

    def add_replacement(self, replacement: RegexReplacement) -> None:
        self.replacements.append(replacement)

    def merge_replacements(self, other: RegexReplacementList) -> None:
        self.replacements += other.replacements

    def first_replacement(self) -> RegexReplacement:
        assert len(self.replacements) > 0
        return self.replacements[0]
