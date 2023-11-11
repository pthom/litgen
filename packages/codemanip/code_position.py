from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CodePosition:
    """Position of an element in the code"""

    line: int = -1
    column: int = -1

    def __str__(self):
        return f"{self.line}:{self.column}"

    @staticmethod
    def from_string(s: str) -> CodePosition:
        """Parses a string like '3:5' which means line 3, column 5"""
        items = s.split(":")
        assert len(items) == 2
        line = int(items[0])
        column = int(items[1])
        r = CodePosition(line, column)
        return r


@dataclass
class CodeContextWithCaret:
    """
    Given a extract of the code, and positions in this code, returns a string that highlight
    this position with a caret "^"

    For example:

            Widget widgets[2];
            ^
    """

    concerned_code_lines: list[str]
    start: CodePosition | None = None
    end: CodePosition | None = None

    def __str__(self) -> str:
        msg = ""
        for i, line in enumerate(self.concerned_code_lines):
            msg += line + "\n"
            if self.start is not None:
                if i == self.start.line:
                    nb_spaces = self.start.column - 1
                    if nb_spaces < 0:
                        nb_spaces = 0
                    msg += " " * nb_spaces + "^" + "\n"
        return msg
