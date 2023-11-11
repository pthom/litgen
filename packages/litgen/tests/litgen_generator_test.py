from __future__ import annotations
from codemanip import code_utils

import litgen


def test_scoping_no_root_namespace():
    """
    In this example, the pydef code should use fully qualified types,
    and the stub code should use loosely qualified types (i.e. minimal typing according to the scope)
    """
    code = """
        namespace N
        {
            struct S {};
            enum class EC { a = 0 };
            enum E { E_a = 0 };

            MY_API EC Foo(EC e = EC::a);
            MY_API E Foo(E e = E_a);
            MY_API S Foo(E e = E_a, S s = S());
        }
    """

    options = litgen.LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    generated_code = litgen.generate_code(options, code)

    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
            { // <namespace N>
                py::module_ pyNsN = m.def_submodule("n", "");
                auto pyNsN_ClassS =
                    py::class_<N::S>
                        (pyNsN, "S", "")
                    .def(py::init<>()) // implicit default constructor
                    ;


                py::enum_<N::EC>(pyNsN, "EC", py::arithmetic(), "")
                    .value("a", N::EC::a, "");


                py::enum_<N::E>(pyNsN, "E", py::arithmetic(), "")
                    .value("a", N::E_a, "");


                pyNsN.def("foo",
                    py::overload_cast<N::EC>(N::Foo), py::arg("e") = N::EC::a);

                pyNsN.def("foo",
                    py::overload_cast<N::E>(N::Foo), py::arg("e") = N::E_a);

                pyNsN.def("foo",
                    py::overload_cast<N::E, N::S>(N::Foo), py::arg("e") = N::E_a, py::arg("s") = N::S());
            } // </namespace N>
    """,
    )

    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        # <submodule n>
        class n:  # Proxy class that introduces typings for the *submodule* n
            pass  # (This corresponds to a C++ namespace. All method are static!)
            class S:
                def __init__(self) -> None:
                    """Auto-generated default constructor"""
                    pass
            class EC(enum.Enum):
                a = enum.auto() # (= 0)
            class E(enum.Enum):
                a = enum.auto() # (= 0)

            @staticmethod
            @overload
            def foo(e: EC = EC.a) -> EC:
                pass
            @staticmethod
            @overload
            def foo(e: E = E.a) -> E:
                pass
            @staticmethod
            @overload
            def foo(e: E = E.a, s: S = S()) -> S:
                pass

        # </submodule n>
    ''',
    )
