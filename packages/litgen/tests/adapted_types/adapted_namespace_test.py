from codemanip import code_utils

import litgen
from litgen import LitgenOptions


def test_adapted_namespace():
    options = LitgenOptions()
    options.namespace_ignored__regex = code_utils.make_regex_exact_word("Main")
    code = code_utils.unindent_code(
        """
void FooRoot();

namespace Main
{
    void FooMain();
    // This is the inner namespace
    namespace Inner
    {
        void FooInner();
    }
}
    """,
        flag_strip_empty_lines=True,
    )

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        def foo_root() -> None:
            pass

        def foo_main() -> None:
            pass

        # <submodule Inner>
        class Inner: # Proxy class that introduces typings for the *submodule* Inner
            # (This corresponds to a C++ namespace. All method are static!)
            """ This is the inner namespace"""
            def foo_inner() -> None:
                pass

        # </submodule Inner>
    ''',
    )

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        m.def("foo_root",
            FooRoot);


        m.def("foo_main",
            Main::FooMain);

        { // <namespace Inner>
            py::module_ pyNamespaceInner = m.def_submodule("Inner", "This is the inner namespace");
            pyNamespaceInner.def("foo_inner",
                Main::Inner::FooInner);
        } // </namespace Inner>
    """,
    )
