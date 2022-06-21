import logging
import os
import sys
from typing import Optional

import pytest  # type: ignore

import litgen
import srcmlcpp
from codemanip import code_utils
from litgen.internal import cpp_to_python, module_pydef_generator
from litgen.options import LitgenOptions, code_style_implot
from srcmlcpp.srcml_types import *


@dataclass
class AdaptedFunction2(CppFunctionDecl):
    function_infos: CppFunctionDecl
    parent_struct_name: str
    cpp_adapter_code: Optional[str] = None
    lambda_to_call: Optional[str] = None

    def __init__(self, function_infos: CppFunctionDecl, parent_struct_name: str):
        self.__dict__ = {**function_infos.__dict__, **self.__dict__}
        self.function_infos = function_infos
        self.parent_struct_name = parent_struct_name
        self.cpp_adapter_code = None
        self.lambda_to_call = None

    def is_method(self):
        return len(self.parent_struct_name) > 0


def test_inherit():
    options = srcmlcpp.SrcmlOptions()
    code = "void Foo();"
    cpp_function = srcmlcpp.code_first_child_of_type(options, CppFunctionDecl, code)
    assert isinstance(cpp_function, CppFunctionDecl)
    a = AdaptedFunction2(cpp_function, "Foo")
