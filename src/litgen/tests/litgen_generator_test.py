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
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
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


            auto pyEnumEC =
                py::enum_<N::EC>(pyNsN, "EC", py::arithmetic(), "")
                    .value("a", N::EC::a, "");


            auto pyEnumE =
                py::enum_<N::E>(pyNsN, "E", py::arithmetic(), "")
                    .value("a", N::E_a, "");


            pyNsN.def("foo",
                py::overload_cast<N::EC>(N::Foo), py::arg("e") = N::EC::a);

            pyNsN.def("foo",
                [](const std::optional<const N::E> & e = std::nullopt) -> N::E
                {
                    auto Foo_adapt_mutable_param_with_default_value = [](const std::optional<const N::E> & e = std::nullopt) -> N::E
                    {

                        const N::E& e_or_default = [&]() -> const N::E {
                            if (e.has_value())
                                return e.value();
                            else
                                return N::E_a;
                        }();

                        auto lambda_result = N::Foo(e_or_default);
                        return lambda_result;
                    };

                    return Foo_adapt_mutable_param_with_default_value(e);
                },
                py::arg("e") = py::none(),
                "---\\nPython bindings defaults:\\n    If e is None, then its default value will be: N.E.a");

            pyNsN.def("foo",
                [](const std::optional<const N::E> & e = std::nullopt, const std::optional<const N::S> & s = std::nullopt) -> N::S
                {
                    auto Foo_adapt_mutable_param_with_default_value = [](const std::optional<const N::E> & e = std::nullopt, const std::optional<const N::S> & s = std::nullopt) -> N::S
                    {

                        const N::E& e_or_default = [&]() -> const N::E {
                            if (e.has_value())
                                return e.value();
                            else
                                return N::E_a;
                        }();

                        const N::S& s_or_default = [&]() -> const N::S {
                            if (s.has_value())
                                return s.value();
                            else
                                return N::S();
                        }();

                        auto lambda_result = N::Foo(e_or_default, s_or_default);
                        return lambda_result;
                    };

                    return Foo_adapt_mutable_param_with_default_value(e, s);
                },
                py::arg("e") = py::none(), py::arg("s") = py::none(),
                "---\\nPython bindings defaults:\\n    If any of the params below is None, then its default value below will be used:\\n        e: N.E.a\\n        s: N.S()");
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
            def foo(e: Optional[E] = None) -> E:
                """---
                Python bindings defaults:
                    If e is None, then its default value will be: N.E.a
                """
                pass
            @staticmethod
            @overload
            def foo(e: Optional[E] = None, s: Optional[S] = None) -> S:
                """---
                Python bindings defaults:
                    If any of the params below is None, then its default value below will be used:
                        e: N.E.a
                        s: N.S()
                """
                pass

        # </submodule n>
    ''',
    )


def test_scoping_enum_in_stub() -> None:
    code = """
    namespace Root
    {
        enum class EC { a = 0, b };

        struct Foo {
            EC e = EC::a;
        };
    }
    """
    options = litgen.LitgenOptions()
    options.fn_params_adapt_mutable_param_with_default_value__regex = r""
    options.namespaces_root = ["Root"]
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class EC(enum.Enum):
            a = enum.auto() # (= 0)
            b = enum.auto() # (= 1)

        class Foo:
            e: EC = EC.a
            def __init__(self, e: EC = EC.a) -> None:
                """Auto-generated default constructor with named params"""
                pass
        '''
    )
