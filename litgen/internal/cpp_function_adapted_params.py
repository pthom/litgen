from typing import List, Optional
from dataclasses import dataclass

from srcmlcpp.srcml_types import CppFunctionDecl


@dataclass
class CppFunctionDeclWithAdaptedParams:
    function_infos: CppFunctionDecl
    parent_struct_name: str
    cpp_adapter_code: Optional[str] = None
    lambda_to_call: Optional[str] = None

    def __init__(self, function_infos: CppFunctionDecl, parent_struct_name: str):
        self.function_infos = function_infos
        self.parent_struct_name = parent_struct_name
        self.cpp_adapter_code = None
        self.lambda_to_call = None

    def is_method(self):
        return len(self.parent_struct_name) > 0


class LambdaAdapter:
    lambda_name: str = ""
    lambda_input_code: str = ""
    lambda_output_code: str = ""

    # If set, will override calls to _make_adapted_lambda_code_end
    # (advanced, currently used by adapt_c_buffers)
    lambda_template_end: Optional[str] = None

    adapted_cpp_parameter_list: List[str] = None
    new_function_infos: Optional[CppFunctionDecl] = None

    def __init__(self):
        self.new_function_infos = None
        self.adapted_cpp_parameter_list = []
