from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen import LitgenOptions


def test_context_namespaces():
    options = LitgenOptions()
    options.namespaces_root = ["Main"]
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


        # <submodule inner>
        class inner:  # Proxy class that introduces typings for the *submodule* inner
            pass  # (This corresponds to a C++ namespace. All method are static!)
            """ This is the inner namespace"""
            @staticmethod
            def foo_inner() -> None:
                pass
            @staticmethod
            def foo_inner2() -> None:
                pass

        # </submodule inner>
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
            py::module_ pyNsInner = m.def_submodule("inner", "This is the inner namespace");
            pyNsInner.def("foo_inner",
                Main::Inner::FooInner);
            pyNsInner.def("foo_inner2",
                Main::Inner::FooInner2);
        } // </namespace Inner>
    """,
    )


def test_context_replacements():
    options = LitgenOptions()
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    code = """
        enum class MyEnumClass
        {
            ValueA = 0,
        };
        enum MyEnumNonClass
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
        '''
        class MyEnumClass(enum.Enum):
            value_a = enum.auto() # (= 0)
        class MyEnumNonClass(enum.Enum):
            value_a = enum.auto() # (= 0)

        def foo_inner(
            x: int = inner.FooValue(),
            a: MyEnumClass = MyEnumClass.value_a,
            b: MyEnumNonClass = MyEnumNonClass.value_a
            ) -> int:
            pass

        # <submodule inner>
        class inner:  # Proxy class that introduces typings for the *submodule* inner
            pass  # (This corresponds to a C++ namespace. All method are static!)
            @staticmethod
            def foo_value() -> int:
                pass

        # </submodule inner>
        ''',
    )
