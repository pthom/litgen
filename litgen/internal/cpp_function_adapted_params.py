from typing import List
from dataclasses import dataclass

from srcmlcpp.srcml_types import CppFunctionDecl


@dataclass
class CppFunctionDeclWithAdaptedParams:
    function_infos: CppFunctionDecl
    cpp_adapter_code: str
    lambda_to_call: str

    def __init__(self, function_infos: CppFunctionDecl):
        self.function_infos = function_infos
        self.cpp_adapter_code = ""
        self.lambda_to_call = ""


class LambdaAdapter:
    lambda_name: str = ""
    lambda_input_code: str = ""
    lambda_output_code: str = ""
    adapted_cpp_parameter_list: List[str] = None
    new_function_infos: CppFunctionDecl = None

    def __init__(self):
        self.new_function_infos = None
        self.adapted_cpp_parameter_list = []
