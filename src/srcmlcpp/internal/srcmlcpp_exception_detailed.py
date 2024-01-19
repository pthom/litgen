from __future__ import annotations
import inspect
import logging
import sys
import traceback

from codemanip import code_utils

from srcmlcpp.srcmlcpp_exception import SrcmlcppException
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions
from srcmlcpp.srcml_wrapper import SrcmlWrapper
from srcmlcpp.scrml_warning_settings import WarningType


class SrcmlcppExceptionDetailed(SrcmlcppException):
    def __init__(self, current_element: SrcmlWrapper, additional_message: str) -> None:
        message = current_element._format_message(additional_message)
        super().__init__(message)


def _get_python_call_info() -> tuple[str, str]:
    stack_lines = traceback.format_stack()
    error_line = stack_lines[-4]
    frame = inspect.currentframe()
    if frame is not None:
        caller_function_name = inspect.getframeinfo(frame.f_back.f_back.f_back).function  # type: ignore
    else:
        caller_function_name = ""
    return caller_function_name, error_line


def show_python_callstack(python_error_line: str) -> str:
    return f"""
            Python call stack info:
    {code_utils.indent_code(python_error_line, 4)}
    """


def emit_warning_if_not_quiet(options: SrcmlcppOptions, message: str, warning_type: WarningType) -> None:
    if options.flag_quiet:
        return
    if warning_type in options.ignored_warnings:
        return
    for ignored_warning_part in options.ignored_warning_parts:
        if ignored_warning_part in message:
            return
    in_pytest = "pytest" in sys.modules
    if in_pytest:
        logging.warning(message)
    else:
        warning_str = f"({warning_type.name}) "
        message = message.replace("Warning: ", "Warning: " + warning_str)
        print(message, file=sys.stderr)
