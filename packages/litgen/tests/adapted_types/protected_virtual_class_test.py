from codemanip import code_utils

import litgen


def test_protected_virtual_class():
    options = litgen.LitgenOptions()
    options.class_expose_protected_methods__regex = "^MyVirtualClass$"
    options.class_override_virtual_methods_in_python__regex = "^MyVirtualClass$"
    options.srcml_options.functions_api_prefixes = "MY_API"
    code = """
        namespace Root
        {
            namespace Inner
            {
                class MyVirtualClass
                {
                public:
                    virtual ~MyVirtualClass() = default;

                    MY_API std::string foo_concrete(int x, const std::string& name)
                    {
                        std::string r =
                              std::to_string(foo_virtual_protected(x))
                            + "_" + std::to_string(foo_virtual_public_pure())
                            + "_" + foo_virtual_protected_const_const(name);
                        return r;
                    }

                    MY_API virtual int foo_virtual_public_pure() const = 0;
                protected:
                    MY_API virtual int foo_virtual_protected(int x) const { return 42 + x; }
                    MY_API virtual std::string foo_virtual_protected_const_const(const std::string& name) const {
                        return std::string("Hello ") + name;
                    }
                };
            }
        }
    """

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        # <submodule Root>
        class Root: # Proxy class that introduces typings for the *submodule* Root
            # (This corresponds to a C++ namespace. All method are static!)

            # <submodule Inner>
            class Inner: # Proxy class that introduces typings for the *submodule* Inner
                # (This corresponds to a C++ namespace. All method are static!)
                class MyVirtualClass:

                    def foo_concrete(self, x: int, name: str) -> str:
                        pass

                    def foo_virtual_public_pure(self) -> int:
                        pass

                    # <protected_methods>
                    def foo_virtual_protected(self, x: int) -> int:
                        pass
                    def foo_virtual_protected_const_const(self, name: str) -> str:
                        pass
                    # </protected_methods>


            # </submodule Inner>

        # </submodule Root>
    """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        { // <namespace Root>
            py::module_ pyNamespaceRoot = m.def_submodule("Root", "");
            { // <namespace Inner>
                py::module_ pyNamespaceRoot_NamespaceInner = pyNamespaceRoot.def_submodule("Inner", "");
                auto pyNamespaceRoot_NamespaceInner_ClassMyVirtualClass =
                    py::class_<Root::Inner::MyVirtualClass, Root::Inner::MyVirtualClass_trampoline>
                        (pyNamespaceRoot_NamespaceInner, "MyVirtualClass", "")
                    .def(py::init<>()) // implicit default constructor
                    .def("foo_concrete",
                        &Root::Inner::MyVirtualClass::foo_concrete, py::arg("x"), py::arg("name"))
                    .def("foo_virtual_public_pure",
                        &Root::Inner::MyVirtualClass::foo_virtual_public_pure)
                    .def("foo_virtual_protected",
                        &Root::Inner::MyVirtualClass_publicist::foo_virtual_protected, py::arg("x"))
                    .def("foo_virtual_protected_const_const",
                        &Root::Inner::MyVirtualClass_publicist::foo_virtual_protected_const_const, py::arg("name"))
                    ;
            } // </namespace Inner>

        } // </namespace Root>
    """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.glue_code,
        """
        namespace Root { namespace Inner {
        // helper type to enable overriding virtual methods in python
        class MyVirtualClass_trampoline : public MyVirtualClass
        {
        public:
            using MyVirtualClass::MyVirtualClass;

            MY_API int foo_virtual_public_pure() const override
            {
                PYBIND11_OVERRIDE_PURE_NAME(
                    MY_API int, // return type
                    Root::Inner::MyVirtualClass, // parent class
                    "foo_virtual_public_pure", // function name (python)
                    foo_virtual_public_pure // function name (c++)
                );
            }
            MY_API int foo_virtual_protected(int x) const override
            {
                PYBIND11_OVERRIDE_NAME(
                    MY_API int, // return type
                    Root::Inner::MyVirtualClass, // parent class
                    "foo_virtual_protected", // function name (python)
                    foo_virtual_protected, // function name (c++)
                    x // params
                );
            }
            MY_API std::string foo_virtual_protected_const_const(const std::string & name) const override
            {
                PYBIND11_OVERRIDE_NAME(
                    MY_API std::string, // return type
                    Root::Inner::MyVirtualClass, // parent class
                    "foo_virtual_protected_const_const", // function name (python)
                    foo_virtual_protected_const_const, // function name (c++)
                    name // params
                );
            }
        };
        } }  // namespace Inner  // namespace Root

        namespace Root { namespace Inner {
        // helper type for exposing protected functions
        class MyVirtualClass_publicist : public MyVirtualClass
        {
        public:
            using MyVirtualClass::foo_virtual_protected;
            using MyVirtualClass::foo_virtual_protected_const_const;
        };
        } }  // namespace Inner  // namespace Root
    """,
    )
