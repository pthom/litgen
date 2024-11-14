import litgen
from srcmlcpp.cpp_types.functions.cpp_parameter import _looks_like_mutable_default_value
from codemanip import code_utils


def test_looks_like_mutable_default_value():
    # Test cases that should be considered immutable
    assert not _looks_like_mutable_default_value("42", None, None)  # Integer literal
    assert not _looks_like_mutable_default_value("-3.14", None, None)  # Float literal
    assert not _looks_like_mutable_default_value("6.022e23", None, None)  # Scientific notation
    assert not _looks_like_mutable_default_value("0x1F", None, None)  # Hexadecimal literal
    assert not _looks_like_mutable_default_value("0b1010", None, None)  # Binary literal
    assert not _looks_like_mutable_default_value("0o77", None, None)  # Octal literal
    assert not _looks_like_mutable_default_value('"immutable_string"', None, None)  # String literal
    assert not _looks_like_mutable_default_value("'c'", None, None)  # Character literal
    assert not _looks_like_mutable_default_value("nullptr", None, None)  # Null pointer
    assert not _looks_like_mutable_default_value("NULL", None, None)  # C-style NULL
    assert not _looks_like_mutable_default_value("true", None, None)  # Boolean literal
    assert not _looks_like_mutable_default_value("false", None, None)  # Boolean literal
    assert not _looks_like_mutable_default_value("nullopt", None, None)  # std::optional null
    assert not _looks_like_mutable_default_value("std::nullopt", None, None)  # std::optional null

    # Test cases that are ambiguous or mutable (heuristic, so return True)
    assert _looks_like_mutable_default_value("[]", None, None)  # List literal (mutable in Python, may translate to array in C++)
    assert _looks_like_mutable_default_value("{}", None, None)  # Empty dictionary/set
    assert _looks_like_mutable_default_value("my_var", None, None)  # Variable reference
    assert _looks_like_mutable_default_value("std::vector<int>()", None, None)  # Default-constructed object
    assert _looks_like_mutable_default_value("SomeClass()", None, None)  # Class instance
    assert _looks_like_mutable_default_value("{1, 2, 3}", None, None)  # Array or initializer list

    # Edge cases with complex literals or expressions
    assert _looks_like_mutable_default_value("3.14 * 2", None, None)  # Expression (should be considered mutable)
    assert _looks_like_mutable_default_value("(int *)nullptr", None, None)  # Cast expression, still ambiguous

    # Trivial immutable types constructors
    assert not _looks_like_mutable_default_value("int()", None, None)  # int()


def test_immutable_literals():
    test_cases = [
        ("1", False),
        ("-42", False),
        ("0", False),
        ("3.14", False),
        ("-2.71f", False),
        ("6.022e23", False),
        ("1.0e-10L", False),
        ("0x1A", False),
        ("0b1010u", False),
        ("'a'", False),
        ('"hello"', False),
        ("nullptr", False),
        ("NULL", False),
        ("true", False),
        ("false", False),
        ("std::nullopt", False),
        # Mutable values
        ("myVar", True),
        ("SomeClass()", True),
        ("[1, 2, 3]", True),
        ("{ 'key': 'value' }", True),
        # trivial_immutable_type_ctor
        ("int()", False),
        ("float()", False),
        ("double()", False),
        ("std::string()", False),
    ]

    for value, expected in test_cases:
        result = _looks_like_mutable_default_value(value, None, None)
        if result != expected:
            raise RuntimeError(f"Test failed for value '{value}': expected {expected}, got {result}")



def test_adapt_mutable_param_with_default_value__class():
    code = """
struct Foo {};
void use_foo(const Foo &foo = Foo());
    """
    options = litgen.LitgenOptions()
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        '''
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            ;


        m.def("use_foo",
            [](const std::optional<const Foo> & foo = std::nullopt)
            {
                auto use_foo_adapt_mutable_param_with_default_value = [](const std::optional<const Foo> & foo = std::nullopt)
                {

                    const Foo& foo_or_default = [&]() -> const Foo {
                        if (foo.has_value())
                            return foo.value();
                        else
                            return Foo();
                    }();

                    use_foo(foo_or_default);
                };

                use_foo_adapt_mutable_param_with_default_value(foo);
            },
            py::arg("foo") = py::none(),
            "---\\nPython bindings defaults:\\n    If foo is None, then its default value will be: Foo()");
        '''
    )

    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Foo:
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass
        def use_foo(foo: Optional[Foo] = None) -> None:
            """---
            Python bindings defaults:
                If foo is None, then its default value will be: Foo()
            """
            pass
        '''
    )


def test_adapt_mutable_param_with_default_value__vector():
    code = """
void use_vec(const std::vector<int>& Ints = std::vector<int>());
    """
    options = litgen.LitgenOptions()
    options.bind_library = litgen.BindLibraryType.nanobind
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        '''
        m.def("use_vec",
            [](const std::optional<const std::vector<int>> & Ints = std::nullopt)
            {
                auto use_vec_adapt_mutable_param_with_default_value = [](const std::optional<const std::vector<int>> & Ints = std::nullopt)
                {

                    const std::vector<int>& Ints_or_default = [&]() -> const std::vector<int> {
                        if (Ints.has_value())
                            return Ints.value();
                        else
                            return std::vector<int>();
                    }();

                    use_vec(Ints_or_default);
                };

                use_vec_adapt_mutable_param_with_default_value(Ints);
            },
            nb::arg("ints") = nb::none(),
            "---\\nPython bindings defaults:\\n    If Ints is None, then its default value will be: List[int]()");
        '''
    )

    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        def use_vec(ints: Optional[List[int]] = None) -> None:
            """---
            Python bindings defaults:
                If Ints is None, then its default value will be: List[int]()
            """
            pass
        '''
    )


def test_adapt_mutable_param_with_default_value__within_struct():
    code = """
    struct Foo
    {
        float       f;   // base immutable type
        bool        b;   // base immutable type
        ImGuiID     id = ImGuiID(15);  // known immutable type
        ScrollFlags flags;  // known immutable type
        ImVec2      v;   // mutable type
    };
    """
    options = litgen.LitgenOptions()
    options.fn_params_adapt_mutable_param_with_default_value__to_autogenerated_named_ctor = True
    def is_immutable(cpp_type: str) -> bool:
        if cpp_type == "ImGuiID":
            return True
        if cpp_type.endswith("Flags"):
            return True
        return False
    options.fn_params_adapt_mutable_param_with_default_value__fn_is_known_immutable_type = is_immutable
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Foo:
            f: float                   # base immutable type
            b: bool                    # base immutable type
            id: ImGuiID = ImGuiID(15)  # known immutable type
            flags: ScrollFlags         # known immutable type
            v: ImVec2                  # mutable type
            def __init__(
                self,
                f: float = float(),
                b: bool = bool(),
                id: ImGuiID = ImGuiID(15),
                flags: ScrollFlags = ScrollFlags(),
                v: Optional[ImVec2] = None
                ) -> None:
                """Auto-generated default constructor with named params
                ---
                Python bindings defaults:
                    If v is None, then its default value will be: ImVec2()
                """
                pass
        '''
    )


def test_adapt_mutable_param_with_default_value__within_struct_2() -> None:
    code = """
    enum class E { A };

    struct Foo { E e = E::A; };
    """
    options = litgen.LitgenOptions()
    options.bind_library = litgen.BindLibraryType.nanobind
    options.fn_params_adapt_mutable_param_with_default_value__to_autogenerated_named_ctor = True
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        '''
        auto pyEnumE =
            nb::enum_<E>(m, "E", nb::is_arithmetic(), "")
                .value("a", E::A, "");


        auto pyClassFoo =
            nb::class_<Foo>
                (m, "Foo", "")
            .def("__init__", [](Foo * self, E e = E::A)
            {
                new (self) Foo();  // placement new
                auto r = self;
                r->e = e;
            },
            nb::arg("e") = E::A
            )
            .def_rw("e", &Foo::e, "")
            ;
        '''
    )


def test_adapt_mutable_param_with_default_value__within_struct_3() -> None:
    code = """
    struct Foo { int a = 1; };
    """
    options = litgen.LitgenOptions()
    options.bind_library = litgen.BindLibraryType.nanobind
    options.fn_params_adapt_mutable_param_with_default_value__to_autogenerated_named_ctor = True
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        '''
        auto pyClassFoo =
            nb::class_<Foo>
                (m, "Foo", "")
            .def("__init__", [](Foo * self, int a = 1)
            {
                new (self) Foo();  // placement new
                auto r = self;
                r->a = a;
            },
            nb::arg("a") = 1
            )
            .def_rw("a", &Foo::a, "")
            ;
        '''
    )


def test__adapt_mutable_param_with_default_value__with_enum() -> None:
    code = """
    namespace Root
    {
        enum class E { A };
        namespace Inner
        {
            void f(E e = E::A);
        }
    }
    """
    options = litgen.LitgenOptions()
    options.bind_library = litgen.BindLibraryType.nanobind
    options.fn_params_adapt_mutable_param_with_default_value__to_autogenerated_named_ctor = True
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        # <submodule root>
        class root:  # Proxy class that introduces typings for the *submodule* root
            pass  # (This corresponds to a C++ namespace. All method are static!)
            class E(enum.Enum):
                a = enum.auto() # (= 0)

            # <submodule inner>
            class inner:  # Proxy class that introduces typings for the *submodule* inner
                pass  # (This corresponds to a C++ namespace. All method are static!)
                @staticmethod
                def f(e: E = E.a) -> None:
                    pass

            # </submodule inner>

        # </submodule root>
        '''
    )
