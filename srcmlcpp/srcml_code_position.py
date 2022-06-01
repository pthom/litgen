from dataclasses import dataclass


@dataclass
class CodePosition:
    """Position of an element in the code"""
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"

    @staticmethod
    def from_string(s: str): # -> CodePosition:
        """Parses a string like '3:5' which means line 3, column 5 """
        items = s.split(":")
        assert len(items) == 2
        line = int(items[0])
        column = int(items[1])
        r = CodePosition(line, column)
        return r

