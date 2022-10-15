from typing import cast
import srcmlcpp
from srcmlcpp.cpp_types import *


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


def test_visible_structs_enums_from_scope():
    code = """
    namespace N1
    {
        struct Foo1 {};
        void f1();

        namespace N2
        {
            struct Foo2a {};
            struct Foo2b {};
            void f2();

            namespace N3
            {
                struct Foo3 {};
                void f3();
            }
        }
    }
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    all_functions = cpp_unit.all_functions_recursive()
    assert len(all_functions) == 3
    f1 = all_functions[0]
    f2 = all_functions[1]
    f3 = all_functions[2]
    assert len(cpp_unit.visible_structs_enums_from_scope(f1.cpp_scope())) == 1
    assert len(cpp_unit.visible_structs_enums_from_scope(f2.cpp_scope())) == 3
    assert len(cpp_unit.visible_structs_enums_from_scope(f3.cpp_scope())) == 4
