from typing import List, Optional
from dataclasses import dataclass
from srcmlcpp.srcml_types import CppFunctionDecl


@dataclass
class AdaptedFunction:
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
