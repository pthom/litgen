from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen import LitgenOptions


# Other tests exist for namespace exist inside litgen_context_test.py
# (since namespaces store their code in the context most of the time)


def test_namespaces():
    options = LitgenOptions()
    options.namespaces_root = ["Main"]
    options.python_run_black_formatter = True
    # options.namespace_exclude__regex  = r"[Ii]nternal|[Dd]etail"  # This is the default value

    # In the code below:
    # - the namespace details should be excluded
    # - the namespace Main should not be outputted as a submodule
    # - the namespace Inner should be produced as a submodule
    # - occurrences of namespace Inner should be grouped
    code = code_utils.unindent_code(
        """
        void FooRoot();

        namespace details // This namespace should be excluded (see options.namespace_exclude__regex)
        {
            void FooDetails();
        }

        namespace // This anonymous namespace should be excluded
        {
            void LocalFunction();
        }

        namespace Main  // This namespace should not be outputted as a submodule
        {
            // this is an inner namespace (this comment should become the namespace doc)
            namespace Inner
            {
                void FooInner();
            }

            // This is a second occurrence of the same inner namespace
            // The generated python module will merge these occurrences
            // (and this comment will be ignored, since the Inner namespace already has a doc)
            namespace Inner
            {
                void FooInner2();
            }
        }
    """,
        flag_strip_empty_lines=True,
    )

    generated_code = litgen.generate_code(options, code)

    # fmt: off
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
            def foo_root() -> None:
                pass





            # <submodule inner>
            class inner:  # Proxy class that introduces typings for the *submodule* inner
                pass  # (This corresponds to a C++ namespace. All method are static!)
                """ this is an inner namespace (this comment should become the namespace doc)"""
                @staticmethod
                def foo_inner() -> None:
                    pass
                @staticmethod
                def foo_inner2() -> None:
                    pass

            # </submodule inner>
        ''',
    )
    # fmt: on

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
            m.def("foo_root",
                FooRoot);

            { // <namespace Inner>
                py::module_ pyNsInner = m.def_submodule("inner", "this is an inner namespace (this comment should become the namespace doc)");
                pyNsInner.def("foo_inner",
                    Main::Inner::FooInner);
                pyNsInner.def("foo_inner2",
                    Main::Inner::FooInner2);
            } // </namespace Inner>
    """,
    )


def test_root_namespace():
    options = LitgenOptions()
    options.namespaces_root = ["Main"]
    code = """
    namespace Main // This namespace should not be outputted as a submodule
    {
        int foo();
    }
    """
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo() -> int:
            pass
    """,
    )
