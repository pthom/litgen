import copy
import sys
from typing import List
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import logging
import traceback, inspect

from litgen import LITGEN_OPTIONS

###########################################
#
# Error and warning messages
#
###########################################

@dataclass
class CodePos:
    line: int = 0
    col: int = 0


@dataclass
class ErrorContext:
    concerned_lines: List[str]
    start: CodePos = CodePos()
    end: CodePos = CodePos()

    def __str__(self):
        msg = ""
        for i, line in enumerate(self.concerned_lines):
            msg += line + "\n"
            if i == self.start.line:
                nb_spaces = self.start.col - 1
                if nb_spaces < 0:
                    nb_spaces = 0
                msg += " " * nb_spaces + "^" + "\n"


        return msg


def _extract_error_context(element: ET.Element) -> ErrorContext:
    from litgen.internal.srcml import srcml_types, srcml_main
    cpp_element = srcml_types.CppElement(element)
    full_code = srcml_main.current_parsed_unit_code()
    full_code_lines = [""] + full_code.split("\n")

    concerned_lines = full_code_lines[cpp_element.start().line : cpp_element.end().line + 1]
    start = CodePos(0, cpp_element.start().column)
    end = CodePos(cpp_element.end().line - cpp_element.start().line, cpp_element.end().column)
    return ErrorContext(concerned_lines, start, end)


def _highlight_responsible_code(element: ET.Element, encoding) -> str:
    from litgen.internal.srcml import srcml_caller
    error_context = _extract_error_context(element)
    return str(error_context)


def _show_element_info(element: ET.Element, encoding):
    from litgen.internal.srcml import srcml_main, srcml_utils
    from litgen.internal import code_utils

    def file_location(element: ET.Element):
        header_filename = srcml_main.current_parsed_file() if len(srcml_main.current_parsed_file()) > 0 else "Position"
        start = srcml_utils.element_start_position(element)
        return f'{header_filename}:{start.line}:{start.column}'


    element_tag = srcml_utils.clean_tag_or_attrib(element.tag)
    concerned_code = _highlight_responsible_code(element, encoding)
    message = f"""        
    While parsing a "{element_tag}", corresponding to this C++ code:
    {file_location(element)}
{code_utils.indent_code(concerned_code, 12)}
    """
    return message


def _warning_detailed_info(
        current_element: ET.Element = None,
        additional_message: str = "",
        encoding: str = "utf-8"
        ):

    from litgen.internal.srcml import srcml_utils, srcml_main, srcml_caller
    from litgen.internal import code_utils

    def _get_python_call_info():
        stack_lines = traceback.format_stack()
        error_line = stack_lines[-4]
        frame = inspect.currentframe()
        caller_function_name = inspect.getframeinfo(frame.f_back.f_back.f_back).function
        return caller_function_name, error_line

    python_caller_function_name, python_error_line = _get_python_call_info()


    def show_python_callstack():
        return f"""
                Python call stack info:
        {code_utils.indent_code(python_error_line, 4)}
        """

    message = ""

    if current_element is not None:
        message += """
        Issue found"""
        message += _show_element_info(current_element, encoding)

    if LITGEN_OPTIONS.flag_show_python_callstack:
        message += show_python_callstack()

    if len(additional_message) > 0:
        message = additional_message + "\n" + code_utils.indent_code(message, 4)

    return message


class SrcMlException(Exception):
    def __init__(self,
                 current_element: ET.Element = None,
                 additional_message = "",
                 encoding: str = "utf-8"
                 ):
        message = _warning_detailed_info(current_element,  additional_message, encoding=encoding)
        super().__init__(message)


def emit_srcml_warning(
        current_element: ET.Element = None,
        additional_message = "",
        encoding:str = "utf-8"
    ):
    if LITGEN_OPTIONS.flag_quiet:
        return
    message = _warning_detailed_info(current_element, additional_message, encoding)

    in_pytest = "pytest" in sys.modules
    if in_pytest:
        logging.warning(message)
    else:
        print(message, file=sys.stderr)


def emit_warning(message: str):
    if LITGEN_OPTIONS.flag_quiet:
        return
    in_pytest = "pytest" in sys.modules
    if in_pytest:
        logging.warning(message)
    else:
        print(message, file=sys.stderr)
