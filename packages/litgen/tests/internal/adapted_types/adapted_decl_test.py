from __future__ import annotations
from codemanip import code_utils

from srcmlcpp import srcmlcpp_main

import litgen
from litgen.internal import LitgenContext
from litgen.internal.adapted_types import AdaptedDecl
from litgen.options import LitgenOptions


def to_adapted_decl(code: str, options: LitgenOptions) -> AdaptedDecl:
    cpp_decl = srcmlcpp_main.code_first_decl(options.srcmlcpp_options, code)
    lg_context = LitgenContext(options)
    adapted_decl = AdaptedDecl(lg_context, cpp_decl)
    return adapted_decl


def test_c_array_fixed_size_to_std_array():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.named_number_macros = {"COUNT": 3}

    code = "const int v[COUNT]"
    adapted_decl = to_adapted_decl(code, options)
    new_adapted_decl = adapted_decl.c_array_fixed_size_to_const_std_array()
    code_utils.assert_are_codes_equal(str(new_adapted_decl.cpp_element()), "const std::array<int, 3>& v")

    code = "const unsigned int v[3]"
    adapted_decl = to_adapted_decl(code, options)
    new_adapted_decl = adapted_decl.c_array_fixed_size_to_const_std_array()
    code_utils.assert_are_codes_equal(str(new_adapted_decl.cpp_element()), "const std::array<unsigned int, 3>& v")

    code = "int v[2]"
    adapted_decl = to_adapted_decl(code, options)
    new_decls = adapted_decl.c_array_fixed_size_to_mutable_new_boxed_decls()
    assert len(new_decls) == 2
    code_utils.assert_are_codes_equal(str(new_decls[0].cpp_element()), "BoxedInt & v_0")
    code_utils.assert_are_codes_equal(str(new_decls[1].cpp_element()), "BoxedInt & v_1")
