from codemanip import code_utils

import litgen
from litgen import LitgenOptions


def test_context_namespaces():
    options = LitgenOptions()
    options.namespace_root__regex = code_utils.make_regex_exact_word("Main")
    # In the code below:
    # - the namespace Main is ignored, but the namespace Inner should be produced as a submodule
    # - occurrences of namespace Inner should be grouped
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

    namespace Inner
    {
        void FooInner2();
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
            def foo_inner2() -> None:
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
            pyNamespaceInner.def("foo_inner2",
                Main::Inner::FooInner2);
        } // </namespace Inner>
    """,
    )


def test_context_replacements():
    options = LitgenOptions()
    options.srcml_options.functions_api_prefixes = "MY_API"
    options.srcml_options.api_suffixes = "MY_API"
    code = """
        enum class MyEnumClass // MY_API
        {
            ValueA = 0,
        };
        enum MyEnumNonClass // MY_API
        {
            MyEnumNonClass_ValueA = 0,
        };
        namespace Inner
        {
            MY_API int FooValue();
        }

        MY_API int FooInner(
            int x = Inner::FooValue(),
            MyEnumClass a = MyEnumClass::ValueA,
            MyEnumNonClass b=  MyEnumNonClass_ValueA);
    """

    # in the generated python stub code:
    #   - usages of MyEnumClass::ValueA should be replaced by MyEnumClass.value_a
    #   - usages of MyEnumNonClass_ValueA should be replaced by MyEnumNonClass.value_a

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class MyEnumClass(Enum):
            value_a = auto() # (= 0)
        class MyEnumNonClass(Enum):
            value_a = auto() # (= 0)

        def foo_inner(
            x: int = Inner.FooValue(),
            a: MyEnumClass = MyEnumClass.value_a,
            b: MyEnumNonClass = MyEnumNonClass.value_a
            ) -> int:
            pass
    """,
    )
