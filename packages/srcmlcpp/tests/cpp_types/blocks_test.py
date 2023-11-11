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


def test_known_elements():
    code = """
            int f();
            constexpr int Global = 0;
            namespace N1
            {
                namespace N2
                {
                    struct S2 { int s2_value = 0; };
                    enum class E2 { a = 0 };  // enum class!
                    int f2();
                }

                namespace N3
                {
                    enum E3 { a = 0 };        // C enum!
                    int f3();

                    // We want to qualify the parameters' declarations of this function
                    void g(
                            int _f = f(),
                            N2::S2 s2 = N2::S2(),
                            N2::E2 e2 = N2::a,      // subtle difference for
                            E3 e3 = E3::a,          // enum and enum class
                            int _f3 = N1::N3::f3(),
                            int other = N1::N4::f4() // unknown function
                        );

                    int n3_value = 0;
                } // namespace N3
            }  // namespace N1
    """
    options = srcmlcpp.SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    known_types = cpp_unit.known_types()
    known_types_names = [k.name() for k in known_types]
    assert known_types_names == ["S2", "E2", "E3"]

    known_callables = cpp_unit.known_callables()
    known_callables_names = [k.name() for k in known_callables]
    assert known_callables_names == ["f", "S2", "f2", "f3", "g"]

    known_callables_init_list = cpp_unit.known_callables_init_list()
    known_callables_init_list_names = [k.name() for k in known_callables_init_list]
    assert known_callables_init_list_names == ["S2"]

    known_values = cpp_unit.known_values()
    known_values_names = [k.name() for k in known_values]
    assert known_values_names == ["Global", "s2_value", "a", "a", "n3_value"]
