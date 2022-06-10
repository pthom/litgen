import logging
import os, sys;

import pytest

_THIS_DIR = os.path.dirname(__file__); sys.path.append(_THIS_DIR + "/../..")

from litgen.internal import code_utils
from litgen.options import CodeStyleOptions, code_style_implot
import litgen
from litgen.internal.function_params_adapter import make_function_params_adapter
from litgen.internal import function_adapt_c_arrays, cpp_to_python
from litgen.internal import module_pydef_generator
import srcmlcpp
from srcmlcpp.srcml_types import *

OPTIONS = litgen.options.code_style_implot()
OPTIONS.srcml_options.functions_api_prefixes = ["MY_API"]


def get_first_function_decl(code) -> CppFunctionDecl:
    cpp_unit = srcmlcpp.code_to_cpp_unit(OPTIONS.srcml_options, code)
    for child in cpp_unit.block_children:
        if isinstance(child, CppFunctionDecl) or isinstance(child, CppFunction):
            return child
    return None


def test_make_function_params_adapter():

    def make_adapted_function(code):
        function_decl = get_first_function_decl(code)
        struct_name = ""
        function_adapted_params = make_function_params_adapter(function_decl, OPTIONS, struct_name)
        return function_adapted_params

    # Easy test with const
    code = """void foo(const int v[2]);"""
    function_adapted_params = make_adapted_function(code)
    code_utils.assert_are_codes_equal(function_adapted_params.function_infos, "void foo(const std::array<int, 2>& v);")

    code = """void foo(unsigned long long v[2]);"""
    function_adapted_params = make_adapted_function(code)
    code_utils.assert_are_codes_equal(function_adapted_params.function_infos, "void foo(std::array<BoxedUnsignedLongLong, 2>& v);")


def test_use_function_params_adapter():
    code = """void truc(const int v[2]);"""
    function_decl = get_first_function_decl(code)
    generated_code = module_pydef_generator._generate_pydef_function(function_decl, OPTIONS)
    # logging.warning("\n" + generated_code)

