from dataclasses import dataclass
from typing import Any

from srcmlcpp.srcml_types import *

from litgen.internal import cpp_to_python
from litgen.options import LitgenOptions


@dataclass
class AdaptedElement:  # (abc.ABC):  # Cannot be abstract (mypy limitation:  https://github.com/python/mypy/issues/5374)
    _cpp_element: CppElementAndComment
    options: LitgenOptions

    def __init__(self, options: LitgenOptions, cpp_element: CppElementAndComment) -> None:
        self._cpp_element = cpp_element
        self.options = options

    def _info_original_location(self, comment_token: str) -> str:
        r = cpp_to_python.info_original_location(self.options, self._cpp_element, comment_token)
        return r

    def info_original_location_cpp(self) -> str:
        return self._info_original_location("//")

    def info_original_location_python(self) -> str:
        return self._info_original_location("#")

    def _str_stub_layout_lines(self, title_lines: List[str], body_lines: List[str] = []) -> List[str]:
        """Common layout for class, enum, and functions stubs
        :param title_lines: class, enum or function decl + function params. Will be followed by docstring
        :param body_lines: body lines for enums and classes, [] for functions
        :return: a list of python code lines for the stub declaration
        """

        # Preprocess: add location on first line
        assert len(title_lines) > 0
        first_line = title_lines[0] + self.info_original_location_python()
        title_lines = [first_line] + title_lines[1:]

        # Preprocess: align comments in body
        if len(body_lines) == 0:
            body_lines = ["pass"]
        body_lines = code_utils.align_python_comments_in_block_lines(body_lines)

        all_lines = title_lines
        docstring_lines = cpp_to_python.docstring_lines(self.options, self.cpp_element())
        all_lines += docstring_lines
        if len(docstring_lines) > 0 and not self.options.python_reproduce_cpp_layout and body_lines != ["pass"]:
            all_lines.append("")

        all_lines += body_lines

        all_lines = code_utils.indent_code_lines(
            all_lines, skip_first_line=True, indent_str=self.options.indent_python_spaces()
        )
        # if not self.options.python_reproduce_cpp_layout:
        #     all_lines.append("")
        return all_lines

    # @abc.abstractmethod
    def cpp_element(self) -> Any:
        # please implement cpp_element in derived classes, it should return the correct CppElement type
        pass

    # @abc.abstractmethod
    def _str_stub_lines(self) -> List[str]:
        raise NotImplementedError()

    # @abc.abstractmethod
    def _str_pydef_lines(self) -> List[str]:
        raise NotImplementedError()

    def comment_pydef_one_line(self) -> str:
        r = cpp_to_python.comment_pydef_one_line(self.options, self._cpp_element.cpp_element_comments.full_comment())
        return r

    def comment_python_shall_place_at_end_of_line(self) -> bool:
        r = cpp_to_python.comment_python_shall_place_at_end_of_line(self.options, self._cpp_element)
        return r

    def comment_python_end_of_line(self) -> str:
        r = cpp_to_python.comment_python_end_of_line(self.options, self._cpp_element)
        return r

    def comment_python_previous_lines(self) -> List[str]:
        r = cpp_to_python.comment_python_previous_lines(self.options, self._cpp_element)
        return r

    def str_stub(self) -> str:
        stub_lines = self._str_stub_lines()
        if len(stub_lines) == 0:
            return ""
        r = "\n".join(stub_lines)
        return r

    def str_pydef(self) -> str:
        pydef_lines = self._str_pydef_lines()
        if len(pydef_lines) == 0:
            return ""
        r = "\n".join(pydef_lines) + "\n"
        return r
