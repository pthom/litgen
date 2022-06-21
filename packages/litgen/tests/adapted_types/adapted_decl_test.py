from srcmlcpp import srcml_main
from srcmlcpp.srcml_types import *

import litgen
from litgen.internal.adapted_types import *
from litgen.options import LitgenOptions


def to_adapted_decl(code, options: LitgenOptions) -> AdaptedDecl:
    cpp_decl = srcml_main.code_first_decl(options.srcml_options, code)
    adapted_decl = AdaptedDecl(cpp_decl, options)
    return adapted_decl


def test_c_array_fixed_size_to_std_array():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"COUNT": 3}

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
