"""Workaround for https://github.com/srcML/srcML/issues/1833

    void Foo(int v = 0 );
is correctly parsed as a function_decl

However,
    void Foo(int v = {} );
is parsed as a decl_stmt
"""
from __future__ import annotations

from typing import Optional

import srcmlcpp
from srcmlcpp.cpp_types import CppDeclStatement
from srcmlcpp.internal import fix_brace_init_default_value


def test_rewrite_decl_if_suspicious_fn_decl():
    def code_first_decl_stmt(code: str) -> CppDeclStatement:
        options = srcmlcpp.SrcmlcppOptions()
        options.fix_brace_init_default_value = False
        cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
        decls = cpp_unit.all_decl_statement_recursive()
        assert len(decls) == 1
        return decls[0]

    def suspicious_code_replacement(code: str) -> Optional[str]:
        decl = code_first_decl_stmt(code)
        return fix_brace_init_default_value._rewrite_decl_if_suspicious_fn_decl(decl)

    assert suspicious_code_replacement("vector<int> v{1,2};") is None
    assert suspicious_code_replacement("std::map<int, int> v{{1, 1}};") is None
    assert suspicious_code_replacement("map<int, int> v{{1, 1}, {2, 2}, { foo(), blah()};") is None
    assert suspicious_code_replacement("S s {.a = 1, .b = 2};") is None
    assert suspicious_code_replacement("void Foo(V v={});") == "void Foo(V v=__srcmlcpp_brace_init__());"
    assert (
        suspicious_code_replacement("void Foo(V v={1, 2}, const Q& q={});")
        == "void Foo(V v=__srcmlcpp_brace_init__(1, 2), const Q& q=__srcmlcpp_brace_init__());"
    )

    options = srcmlcpp.SrcmlcppOptions()
    c = suspicious_code_replacement("void Foo(V v={});")
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, c)
    assert len(cpp_unit.all_functions_recursive()) == 1

    c = suspicious_code_replacement("void Foo(V v={1, 2}, const Q& q={});")
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, c)
    assert len(cpp_unit.all_functions_recursive()) == 1


def test_change_decl_stmt_to_function_decl_if_suspicious():
    options = srcmlcpp.SrcmlcppOptions()

    code = "void Foo(V v = {});"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1
    assert str(functions[0]) == "void Foo(V v = {});"

    code = "void Foo(V v={});"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1
    assert str(functions[0]) == "void Foo(V v = {});"

    code = "void Foo(V v={1, 2}, const Q& q={});"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1
    assert str(functions[0]) == "void Foo(V v = {1, 2}, const Q & q = {});"


def test_change_macro_to_constructor():
    code = """
        struct S {
            S(V v = {});
        };
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1

    code = """
    struct S {
        S(Point3D p = {1.f, 2.f, 3.f});
    };
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    functions = cpp_unit.all_functions_recursive()
    assert len(functions) == 1
    assert functions[0].is_constructor()


def test_2():
    options = srcmlcpp.SrcmlcppOptions()
    code = "int FnBrace(S s = {}) { return 1;}"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    assert len(cpp_unit.all_functions_recursive()) == 1
