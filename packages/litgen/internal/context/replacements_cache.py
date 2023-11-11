from __future__ import annotations
from codemanip.code_replacements import RegexReplacement, RegexReplacementList


class ReplacementsCache:
    """
    Store replacements gathered from the code base:
        for example, enum member names, static class members, function names, for which a conversion from
        CamelCase to snake_case might have been applied
    """

    replacement_list: RegexReplacementList = RegexReplacementList()

    def store_replacements(self, replacements: RegexReplacementList) -> None:
        self.replacement_list.merge_replacements(replacements)

    def store_replacement(self, replacement: RegexReplacement) -> None:
        self.replacement_list.replacements.append(replacement)

    def apply(self, s: str) -> str:
        return self.replacement_list.apply(s)
