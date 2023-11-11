"""Workaround for https://github.com/srcML/srcML/issues/1833

    void Foo(int v = 0 );
is correctly parsed as a function_decl

However,
    void Foo(int v = {} );
is parsed as a decl_stmt
"""
from __future__ import annotations

import litgen
from codemanip import code_utils


def test_fn_brace():
    code = "void f(V v={1, 2});"
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("f",
            f, py::arg("v") = V{1, 2});
        """,
    )
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def f(v: V = V(1, 2)) -> None:
            pass
        """,
    )


def test_struct_brace():
    code = """
        struct Foo {
            std::vector<int> l={1};
            V v = {1, 2, 3};
        };
    """
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "")
            .def(py::init<>([](
            std::vector<int> l = {1}, V v = {1, 2, 3})
            {
                auto r = std::make_unique<Foo>();
                r->l = l;
                r->v = v;
                return r;
            })
            , py::arg("l") = std::vector<int>{1}, py::arg("v") = V{1, 2, 3}
            )
            .def_readwrite("l", &Foo::l, "")
            .def_readwrite("v", &Foo::v, "")
            ;
            """,
    )

    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Foo:
            l: List[int] = List[int](1)
            v: V = V(1, 2, 3)
            def __init__(self, l: List[int] = List[int](1), v: V = V(1, 2, 3)) -> None:
                """Auto-generated default constructor with named params"""
                pass
        ''',
    )
