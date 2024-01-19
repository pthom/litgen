from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from codemanip import code_utils
from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp.cpp_types import CppElementAndComment, CppUnit

from litgen.internal import cpp_to_python
from litgen.internal.context.litgen_context import LitgenContext
from litgen.options import LitgenOptions


_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS = "litgen:   Create AdaptedElements............. "
_PROGRESS_BAR_TITLE_PYDEF = "litgen:   Generate pydef cpp file............ "
_PROGRESS_BAR_TITLE_STUB = "litgen:   Generate stubs..................... "


@dataclass
class AdaptedElement:  # (abc.ABC):  # Cannot be abstract (mypy limitation:  https://github.com/python/mypy/issues/5374)
    """AdaptedElement: base class of all the Cpp element that can be outputted as pydef + stub files

    This is an abstract class! Each of its derived classes (AdaptedClass, AdaptedFunction, AdaptedCppUnit, etc.) must:
        - implement `_str_pydef_lines`, which will fill the C++ binding code for this derived class
        - implement `_str_stub_lines`, which will fill the python stub code  for this derived class

    Some derived classes may add information into the context (lg_context), for example:
        - list of the encountered namespaces code (which will be dumped at the end)
        - list of encountered "boxed types"
    """

    #  ============================================================================================
    #
    #    Members
    #
    #  ============================================================================================

    # The adapted CppElement (can be a CppClass, CppFunctionDecl, etc.)
    _cpp_element: CppElementAndComment
    # Generation options
    options: LitgenOptions
    # Context were some additional namespace and boxed types info
    # can be stored during creation of the tree of AdaptedElements
    lg_context: LitgenContext

    #  ============================================================================================
    #
    #    Init
    #
    #  ============================================================================================

    def __init__(self, lg_context: LitgenContext, cpp_element: CppElementAndComment) -> None:
        self._cpp_element = cpp_element
        self.lg_context = lg_context
        self.options = lg_context.options
        element_line = cpp_element.start().line
        if isinstance(self._cpp_element, CppUnit):
            assert self._cpp_element.parent is None
        else:
            assert self._cpp_element.parent is not None
        global_progress_bars().set_current_line(_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS, element_line)

    #  ============================================================================================
    #
    #    Abstract methods that shall be implemented by derived classes
    #
    #  ============================================================================================

    # @abc.abstractmethod
    def cpp_element(self) -> Any:
        # please implement cpp_element in derived classes, it should return
        #     `cast(AdaptedXXX, self._cpp_element)`
        pass

    # @abc.abstractmethod
    def stub_lines(self) -> list[str]:
        """
        This is an abstract class! Each of its derived classes (AdaptedClass, AdaptedFunction, AdaptedCppUnit, etc.) must:
            - implement `_str_pydef_lines`, which will fill the C++ binding code for this derived class
            - implement `_str_stub_lines`, which will fill the python stub code  for this derived class
        """
        raise NotImplementedError()

    # @abc.abstractmethod
    def pydef_lines(self) -> list[str]:
        """
        This is an abstract class! Each of its derived classes (AdaptedClass, AdaptedFunction, AdaptedCppUnit, etc.) must:
            - implement `_str_pydef_lines`, which will fill the C++ binding code for this derived class
            - implement `_str_stub_lines`, which will fill the python stub code  for this derived class
        """
        raise NotImplementedError()

    #  ============================================================================================
    #
    #    Main interface: str_stub() and str_pydef() return the generated code
    #    They will be called for an AdaptedUnit (i.e. a fully adapted C++ file)
    #
    #  ============================================================================================

    def str_stub(self) -> str:
        stub_lines = self.stub_lines()
        if len(stub_lines) == 0:
            return ""
        r = "\n".join(stub_lines)
        return r

    def str_pydef(self) -> str:
        pydef_lines = self.pydef_lines()
        if len(pydef_lines) == 0:
            return ""
        r = "\n".join(pydef_lines) + "\n"
        return r

    #  ============================================================================================
    #
    #    Utilities used by derived classes
    #
    #    Methods prefix: _elm_
    #
    #  ============================================================================================

    def _elm_comment_pydef_one_line(self) -> str:
        r = cpp_to_python.comment_pydef_one_line(self.options, self._cpp_element.cpp_element_comments.full_comment())
        return r

    def _elm_comment_python_shall_place_at_end_of_line(self) -> bool:
        r = cpp_to_python.comment_python_shall_place_at_end_of_line(self.options, self._cpp_element)
        return r

    def _elm_comment_python_end_of_line(self) -> str:
        r = cpp_to_python.comment_python_end_of_line(self.options, self._cpp_element)
        return r

    def _elm_comment_python_previous_lines(self) -> list[str]:
        r = cpp_to_python.comment_python_previous_lines(self.options, self._cpp_element)
        return r

    def _elmpriv_info_original_location(self, comment_token: str) -> str:
        r = cpp_to_python.info_original_location(self.options, self._cpp_element, comment_token)
        return r

    def _elm_info_original_location_cpp(self) -> str:
        return self._elmpriv_info_original_location("//")

    def _elm_info_original_location_python(self) -> str:
        return self._elmpriv_info_original_location("#")

    def _elm_stub_original_code_lines_info(self) -> list[str]:
        if not self.options.original_signature_flag_show:
            return []

        cpp_original_code = self._cpp_element.str_code_verbatim()
        cpp_original_code = code_utils.strip_empty_lines(cpp_original_code)
        if len(cpp_original_code) == 0:
            return []
        else:
            cpp_original_code_lines = cpp_original_code.split("\n")
            cpp_original_code_lines = list(map(lambda s: "# " + s, cpp_original_code_lines))
            cpp_original_code_lines[0] += "    /* original C++ signature */"
            return cpp_original_code_lines

    def _elm_str_stub_layout_lines(self, title_lines: list[str], body_lines: Optional[list[str]] = None) -> list[str]:
        """Common layout for class, enum, and functions stubs
        :param title_lines: class, enum or function decl + function params. Will be followed by docstring
        :param body_lines: body lines for enums and classes, [] for functions
        :return: a list of python code lines for the stub declaration
        """

        # Preprocess: add location on first line
        assert len(title_lines) > 0
        first_line = title_lines[0] + self._elm_info_original_location_python()
        title_lines = [first_line] + title_lines[1:]

        # Preprocess: align comments in body
        if body_lines is None or (isinstance(body_lines, list) and len(body_lines) == 0):
            body_lines = ["pass"]
        body_lines = code_utils.align_python_comments_in_block_lines(body_lines)

        all_lines = title_lines
        docstring_lines = cpp_to_python.docstring_lines(self.options, self.cpp_element())
        all_lines += docstring_lines
        if len(docstring_lines) > 0 and not self.options.python_reproduce_cpp_layout and body_lines != ["pass"]:
            all_lines.append("")

        all_lines += body_lines

        all_lines = code_utils.indent_code_lines(
            all_lines, skip_first_line=True, indent_str=self.options._indent_python_spaces()
        )

        return all_lines
