from codemanip.code_replacements import RegexReplacementList


class ReplacementsCache:
    """
    Store global replacements gathered from the code base
    (for example, enum member names, static class members, etc)

    This is work in progress, and should become a member of LitgenContext
    """

    replacement_list: RegexReplacementList = RegexReplacementList()

    def store_static_member_value_replacements(self, replacements: RegexReplacementList):
        self.replacement_list.merge_replacements(replacements)

    def apply(self, s: str) -> str:
        return self.replacement_list.apply(s)


_CACHE = ReplacementsCache()


def apply_cached_replacement(s: str) -> str:
    return _CACHE.apply(s)


def store_replacement(r: RegexReplacementList):
    _CACHE.replacement_list.merge_replacements(r)
