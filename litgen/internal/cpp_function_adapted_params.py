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
        self.lambda_to_call = self.function_infos.name
