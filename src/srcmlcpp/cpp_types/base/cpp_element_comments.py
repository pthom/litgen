from __future__ import annotations
from dataclasses import dataclass


__all__ = ["CppElementComments"]


@dataclass
class CppElementComments:
    """Gathers the C++ comments about functions, declarations, etc. : each CppElement can store
     comment on previous lines, and a single line comment next to its declaration.

    Lonely comments are stored as `CppComment`

     Example:
         ````cpp
         /*
         A multiline C comment
         about Foo1
         */
         void Foo1();

         // First line of comment on Foo2()
         // Second line of comment on Foo2()
         void Foo2();

         // A lonely comment

         //
         // Another lonely comment, on two lines
         // which ends on this second line, but has surrounding empty lines
         //

         // A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment
         // since Foo3 and Foo4 have eol comments
         Void Foo3(); // Comment on end of line for Foo3()
         Void Foo4(); // Comment on end of line for Foo4()
         // A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())
         ```
    """

    comment_on_previous_lines: str
    comment_end_of_line: str
    is_c_style_comment: bool  # Will be True if comment_on_previous_lines was a /* */ comment

    def __init__(self) -> None:
        self.comment_on_previous_lines = ""
        self.comment_end_of_line = ""
        self.is_c_style_comment = False

    @staticmethod
    def from_comments(
        comment_on_previous_lines: str = "", comment_end_of_line: str = "", format_comments: bool = True
    ) -> CppElementComments:
        if format_comments:
            if len(comment_on_previous_lines) > 0:
                comment_on_previous_lines = "// " + "\n// ".join(comment_on_previous_lines.split("\n"))
                if not comment_on_previous_lines.endswith("\n"):
                    comment_on_previous_lines += "\n"
            if len(comment_end_of_line) > 0:
                comment_end_of_line = " // " + comment_end_of_line.replace("\n", " | ")

        r = CppElementComments()
        r.comment_on_previous_lines = comment_on_previous_lines
        r.comment_end_of_line = comment_end_of_line
        r.is_c_style_comment = r.comment_on_previous_lines.startswith("/*")
        return r

    def top_comment_code(self, add_eol: bool = True, preserve_c_style_comment: bool = True) -> str:
        if preserve_c_style_comment and self.is_c_style_comment:
            r = "/*" + self.comment_on_previous_lines + "*/"
            return r

        def add_line_comment_token_if_needed(comment_line: str) -> str:
            if not comment_line.strip().startswith("//"):
                return "//" + comment_line
            else:
                return comment_line

        top_comments = map(add_line_comment_token_if_needed, self.comment_on_previous_lines.splitlines())
        top_comment = "\n".join(top_comments)
        if add_eol:
            if len(top_comment) > 0:
                if not top_comment.endswith("\n"):
                    top_comment += "\n"
        else:
            while top_comment.endswith("\n"):
                top_comment = top_comment[:-1]
        return top_comment

    def eol_comment_code(self) -> str:
        if len(self.comment_end_of_line) == 0:
            return ""
        else:
            if self.comment_end_of_line.strip().startswith("//"):
                return self.comment_end_of_line
            else:
                return " //" + self.comment_end_of_line

    def add_eol_comment(self, comment: str) -> None:
        if len(self.comment_end_of_line) == 0:
            self.comment_end_of_line = comment
        else:
            self.comment_end_of_line += " - " + comment

    def add_comment_on_previous_lines(self, comment: str) -> None:
        if len(self.comment_on_previous_lines) == 0:
            self.comment_on_previous_lines = comment
        else:
            self.comment_on_previous_lines += "\n" + comment

    def full_comment(self) -> str:
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line

    def comments_as_str(self) -> str:
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line
