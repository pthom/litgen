# pyright: reportAttributeAccessIssue=false
from __future__ import annotations
from typing import cast
import srcmlcpp
from srcmlcpp.cpp_types import CppNamespace


def test_block():
    code = """
    struct Foo
    {
    public:
        int a = 0;
        int foo();
    };
    namespace Ns
    {
        int dummy();
        struct Foo2 {
            Foo2(); // will count as function in the recursive count
        };
        int inner_f();
    }

    int f();
    int f(int x);
    int g();
    """

    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.srcmlcpp_main.code_to_cpp_unit(options, code)
    assert len(cpp_unit.all_structs_recursive()) == 2

    namespaces = cpp_unit.all_elements_of_type(CppNamespace)
    assert len(namespaces) == 1

    ns = cast(CppNamespace, namespaces[0])
    foo2 = ns.block.find_struct_or_class("Foo2")
    assert foo2 is not None

    foo2_from_main = cpp_unit.find_struct_or_class("Foo2")
    assert foo2_from_main is None
    foo2_from_main = cpp_unit.find_struct_or_class("Foo2", ns.block.cpp_scope())
    assert foo2_from_main is not None

    functions_recursive = cpp_unit.all_functions_recursive()
    assert len(functions_recursive) == 7

    functions = cpp_unit.all_functions()
    assert len(functions) == 3

    # int f();
    # int f(int x);
    # int g();
    f0 = functions[0]
    f1 = functions[1]
    g = functions[2]
    assert cpp_unit.is_function_overloaded(f0)
    assert cpp_unit.is_function_overloaded(f1)
    assert not cpp_unit.is_function_overloaded(g)
