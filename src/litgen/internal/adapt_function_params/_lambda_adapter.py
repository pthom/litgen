from __future__ import annotations
from typing import Optional

from srcmlcpp.cpp_types import CppFunctionDecl


class LambdaAdapter:
    lambda_name: str = ""
    lambda_input_code: str = ""
    lambda_output_code: str = ""

    # If set, will override calls to _make_adapted_lambda_code_end
    # (advanced, currently used by adapt_c_buffers)
    lambda_template_end: Optional[str] = None

    adapted_cpp_parameter_list: list[str] = []
    new_function_infos: Optional[CppFunctionDecl] = None

    def __init__(self) -> None:
        self.new_function_infos = None
        self.adapted_cpp_parameter_list = []
