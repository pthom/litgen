from typing import Tuple
import traceback
import inspect
import logging
import sys

from codemanip import code_utils

from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_exception import SrcmlException
from srcmlcpp.srcml_wrapper import SrcmlWrapper


class SrcmlExceptionDetailed(SrcmlException):
    def __init__(self, current_element: SrcmlWrapper, additional_message: str) -> None:
        message = current_element._format_message(additional_message)
        super().__init__(message)


def _get_python_call_info() -> Tuple[str, str]:
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


def emit_warning_if_not_quiet(options: SrcmlOptions, message: str) -> None:
    if options.flag_quiet:
        return
    in_pytest = "pytest" in sys.modules
    if in_pytest:
        logging.warning(message)
    else:
        if not message.startswith("Warning"):
            message = "Warning:" + message
        print(message, file=sys.stderr)
