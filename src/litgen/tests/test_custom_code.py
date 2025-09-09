import litgen
from codemanip import code_utils


def test_custom_code():
    code = """
    namespace RootNs{
    struct Foo
    {
        int mValue = 0;
    };
    }
    """
    options = litgen.LitgenOptions()
    options.bind_library = litgen.BindLibraryType.nanobind

    options.custom_bindings.add_custom_bindings_to_class(
        qualified_class="RootNs::Foo",
        stub_code='''
            def get_value(self) -> int:
                """Get the value"""
                ...
            def set_value(self, value: int) -> None:
                """Set the value"""
                ...
        ''',
        pydef_code="""
            LG_CLASS.def("get_value", [](const RootNs::Foo& self){ return self.mValue; });
            LG_CLASS.def("set_value", [](RootNs::Foo& self, int value){ self.mValue = value; }, nb::arg("value"));
        """,
    )

    options.custom_bindings.add_custom_bindings_to_submodule(
        qualified_namespace="RootNs",
        stub_code='''
        @staticmethod
        def foo_namespace_function() -> None:
            """A custom function in the submodule"""
            ...
        ''',
        pydef_code="""
        // Example of adding a custom function to the submodule
        LG_SUBMODULE.def("foo_namespace_function", [](){ std::cout << "Hello from foo_namespace_function!" << std::endl; });
        """,
    )

    options.custom_bindings.add_custom_bindings_to_main_module(
        stub_code='''
        def global_function() -> None:
            """A custom function in the global namespace"""
            ...
        ''',
        pydef_code="""
        // Example of adding a custom function to the main module
        LG_MODULE.def("global_function", [](){ std::cout << "Hello from global_function!" << std::endl; });
        """,
    )

    generated_code = litgen.generate_code(options, code)

    # print("\n" + generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
            # <submodule root_ns>
            class root_ns:  # Proxy class that introduces typings for the *submodule* root_ns
                pass  # (This corresponds to a C++ namespace. All method are static!)
                class Foo:
                    m_value: int = 0
                    def __init__(self, m_value: int = 0) -> None:
                        """Auto-generated default constructor with named params"""
                        pass

                    def get_value(self) -> int:
                        """Get the value"""
                        ...
                    def set_value(self, value: int) -> None:
                        """Set the value"""
                        ...


                @staticmethod
                def foo_namespace_function() -> None:
                    """A custom function in the submodule"""
                    ...
            # </submodule root_ns>

            def global_function() -> None:
                """A custom function in the global namespace"""
                ...
    ''')

    # print("\n" + generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        '''
            { // <namespace RootNs>
                nb::module_ pyNsRootNs = m.def_submodule("root_ns", "");
                auto pyNsRootNs_ClassFoo =
                    nb::class_<RootNs::Foo>
                        (pyNsRootNs, "Foo", "")
                    .def("__init__", [](RootNs::Foo * self, int mValue = 0)
                    {
                        new (self) RootNs::Foo();  // placement new
                        auto r_ctor_ = self;
                        r_ctor_->mValue = mValue;
                    },
                    nb::arg("m_value") = 0
                    )
                    .def_rw("m_value", &RootNs::Foo::mValue, "")
                    ;

                pyNsRootNs_ClassFoo.def("get_value", [](const RootNs::Foo& self){ return self.mValue; });
                pyNsRootNs_ClassFoo.def("set_value", [](RootNs::Foo& self, int value){ self.mValue = value; }, nb::arg("value"));



                // Example of adding a custom function to the submodule
                pyNsRootNs.def("foo_namespace_function", [](){ std::cout << "Hello from foo_namespace_function!" << std::endl; });
            } // </namespace RootNs>

            // Example of adding a custom function to the main module
            m.def("global_function", [](){ std::cout << "Hello from global_function!" << std::endl; });
    ''')
