from __future__ import annotations
from codemanip import code_utils

import litgen
from litgen import BindLibraryType
from litgen.litgen_generator import LitgenGeneratorTestsHelper
from litgen.options import LitgenOptions


def log_code(code: str) -> None:
    import logging

    logging.warning(f"\n>>>{code}<<<")


def test_struct_stub_layouts():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.named_number_macros = {"MY_VALUE": 256}

    code = """
// Doc about Foo
struct Foo
{
    // Doc about members
    int a;      // Doc about a
    bool flag;  // Doc about flag


    // Doc about Methods
    int add(int v) { return v + a; } // Simple addition
};
    """

    options.python_reproduce_cpp_layout = True
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # log_code(stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo:
            """ Doc about Foo"""
            # Doc about members
            a: int      # Doc about a
            flag: bool  # Doc about flag


            # Doc about Methods
            def add(self, v: int) -> int:
                """ Simple addition"""
                pass
            def __init__(self, a: int = int(), flag: bool = bool()) -> None:
                """Auto-generated default constructor with named params"""
                pass
     ''',
    )

    options.python_reproduce_cpp_layout = False
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # log_code(stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo:
            """ Doc about Foo"""

            # Doc about members

            # Doc about a
            a: int
            # Doc about flag
            flag: bool

            # Doc about Methods

            def add(self, v: int) -> int:
                """ Simple addition"""
                pass
            def __init__(self, a: int = int(), flag: bool = bool()) -> None:
                """Auto-generated default constructor with named params"""
                pass
    ''',
    )


def test_struct_pydef_simple():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.named_number_macros = {"MY_VALUE": 256}
    code = """
        // Doc about Foo
        struct Foo
        {
            // Doc about members
            int a;      // Doc about a
            bool flag;  // Doc about flag


            // Doc about Methods
            int add(int v) { return v + a; } // Simple addition
        };
    """

    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # log_code(pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "Doc about Foo")
            .def(py::init<>([](
            int a = int(), bool flag = bool())
            {
                auto r = std::make_unique<Foo>();
                r->a = a;
                r->flag = flag;
                return r;
            })
            , py::arg("a") = int(), py::arg("flag") = bool()
            )
            .def_readwrite("a", &Foo::a, "Doc about a")
            .def_readwrite("flag", &Foo::flag, "Doc about flag")
            .def("add",
                &Foo::add,
                py::arg("v"),
                "Simple addition")
            ;
        """,
    )


def test_struct_stub_complex():
    options = LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    code = """
        // A dummy class that handles 4 channel float colors
        class Color4
        {
        public:
            Color4(const float values[4]);

            // Return the color as a float gray value
            MY_API float ToGray() const;
            // Returns true if the color is pure black
            MY_API bool IsBlack() const;

            // Members
            bool  flag_BGRA = false;  // true if color order is BGRA
            float Components[4];    // A numeric C array that will be published as a numpy array
            Widget widgets[2]; // an array that cannot be published, as it does not contain numeric elements
        private:
            int _priv_value; // a private member that will not be published
        };
    """

    options.python_reproduce_cpp_layout = True
    stub_code = LitgenGeneratorTestsHelper.code_to_stub(options, code)
    # log_code(stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Color4:
            """ A dummy class that handles 4 channel float colors"""
            def __init__(self, values: List[float]) -> None:
                pass

            def to_gray(self) -> float:
                """ Return the color as a float gray value"""
                pass
            def is_black(self) -> bool:
                """ Returns True if the color is pure black"""
                pass

            # Members
            flag_bgra: bool = False  # True if color order is BGRA
            components: np.ndarray   # ndarray[type=float, size=4]  # A numeric C array that will be published as a numpy array
    ''',
    )

    pydef_code = LitgenGeneratorTestsHelper.code_to_pydef(options, code)
    # log_code(pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassColor4 =
            py::class_<Color4>
                (m, "Color4", "A dummy class that handles 4 channel float colors")
            .def(py::init(
                [](const std::array<float, 4>& values) -> std::unique_ptr<Color4>
                {
                    auto ctor_wrapper = [](const float values[4]) ->  std::unique_ptr<Color4>
                    {
                        return std::make_unique<Color4>(values);
                    };
                    auto ctor_wrapper_adapt_fixed_size_c_arrays = [&ctor_wrapper](const std::array<float, 4>& values) -> std::unique_ptr<Color4>
                    {
                        auto lambda_result = ctor_wrapper(values.data());
                        return lambda_result;
                    };

                    return ctor_wrapper_adapt_fixed_size_c_arrays(values);
                }),     py::arg("values"))
            .def("to_gray",
                &Color4::ToGray, "Return the color as a float gray value")
            .def("is_black",
                &Color4::IsBlack, "Returns True if the color is pure black")
            .def_readwrite("flag_bgra", &Color4::flag_BGRA, "True if color order is BGRA")
            .def_property("components",
                [](Color4 &self) -> pybind11::array
                {
                    auto dtype = pybind11::dtype(pybind11::format_descriptor<float>::format());
                    auto base = pybind11::array(dtype, {4}, {sizeof(float)});
                    return pybind11::array(dtype, {4}, {sizeof(float)}, self.Components, base);
                }, [](Color4& self) {},
                "A numeric C array that will be published as a numpy array")
            ;
        """,
    )


def test_templated_class():
    code = """
    template<typename T>
    struct MyTemplateClass
    {
        std::vector<T> values;

        // Standard constructor
        MyTemplateClass() {}

        // Constructor that will need a parameter adaptation
        MyTemplateClass(const T v[2]);

        // Standard method
        T sum();

        // Method that requires a parameter adaptation
        T sum2(const T v[2]);
    };
    """

    options = LitgenOptions()
    options.class_template_options.add_specialization(
        name_regex="^MyTemplateClass", cpp_types_list_str=["std::string"], cpp_synonyms_list_str=[]
    )

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        #  ------------------------------------------------------------------------
        #      <template specializations for class MyTemplateClass>
        class MyTemplateClass_string:  # Python specialization for MyTemplateClass<std::string>
            values: List[str]

            @overload
            def __init__(self) -> None:
                """ Standard constructor"""
                pass

            @overload
            def __init__(self, v: List[str]) -> None:
                """ Constructor that will need a parameter adaptation"""
                pass

            def sum(self) -> str:
                """ Standard method"""
                pass

            def sum2(self, v: List[str]) -> str:
                """ Method that requires a parameter adaptation"""
                pass
        #      </template specializations for class MyTemplateClass>
        #  ------------------------------------------------------------------------
    ''',
    )

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassMyTemplateClass_string =
            py::class_<MyTemplateClass<std::string>>
                (m, "MyTemplateClass_string", "")
            .def_readwrite("values", &MyTemplateClass<std::string>::values, "")
            .def(py::init<>(),
                "Standard constructor")
            .def(py::init(
                [](const std::array<std::string, 2>& v) -> std::unique_ptr<MyTemplateClass<std::string>>
                {
                    auto ctor_wrapper = [](const std::string v[2]) ->  std::unique_ptr<MyTemplateClass<std::string>>
                    {
                        return std::make_unique<MyTemplateClass<std::string>>(v);
                    };
                    auto ctor_wrapper_adapt_fixed_size_c_arrays = [&ctor_wrapper](const std::array<std::string, 2>& v) -> std::unique_ptr<MyTemplateClass<std::string>>
                    {
                        auto lambda_result = ctor_wrapper(v.data());
                        return lambda_result;
                    };

                    return ctor_wrapper_adapt_fixed_size_c_arrays(v);
                }),
                py::arg("v"),
                "Constructor that will need a parameter adaptation")
            .def("sum",
                &MyTemplateClass<std::string>::sum, "Standard method")
            .def("sum2",
                [](MyTemplateClass<std::string> & self, const std::array<std::string, 2>& v) -> std::string
                {
                    auto sum2_adapt_fixed_size_c_arrays = [&self](const std::array<std::string, 2>& v) -> std::string
                    {
                        auto lambda_result = self.sum2(v.data());
                        return lambda_result;
                    };

                    return sum2_adapt_fixed_size_c_arrays(v);
                },
                py::arg("v"),
                "Method that requires a parameter adaptation")
            ;
    """,
    )


def test_deepcopy_simple():
    # Note: there are lots of other tests inside litgen/integration_tests/mylib/class_copy_test.h
    code = "struct Foo {};"
    options = litgen.LitgenOptions()
    options.class_deep_copy__regex = r".*"
    options.class_copy__regex = r".*"
    options.class_copy_add_info_in_stub = True
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "\\n(has support for copy.copy and copy.deepcopy)")
            .def(py::init<>()) // implicit default constructor
            .def("__copy__",  [](const Foo &self) {
                return Foo(self);
            })
            .def("__deepcopy__",  [](const Foo &self, py::dict) {
                return Foo(self);
            }, py::arg("memo"))    ;
    """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Foo:
            """
            (has support for copy.copy and copy.deepcopy)
            """
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass
    ''',
    )


def test_deepcopy_with_specialization():
    code = """
    namespace Ns
    {
        template<typename T>
        struct Foo
        {
            T value;
        };
    }
    """
    options = litgen.LitgenOptions()
    options.class_template_options.add_specialization(".*", ["int"], [])
    options.class_deep_copy__regex = r".*"
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        { // <namespace Ns>
            py::module_ pyNsNs = m.def_submodule("ns", "");
            auto pyNsNs_ClassFoo_int =
                py::class_<Ns::Foo<int>>
                    (pyNsNs, "Foo_int", "")
                .def(py::init<>([](
                int value = int())
                {
                    auto r = std::make_unique<Ns::Foo<int>>();
                    r->value = value;
                    return r;
                })
                , py::arg("value") = int()
                )
                .def_readwrite("value", &Ns::Foo<int>::value, "")
                .def("__deepcopy__",  [](const Ns::Foo<int> &self, py::dict) {
                    return Ns::Foo<int>(self);
                }, py::arg("memo"))    ;
        } // </namespace Ns>
    """,
    )

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        # <submodule ns>
        class ns:  # Proxy class that introduces typings for the *submodule* ns
            pass  # (This corresponds to a C++ namespace. All method are static!)
            #  ------------------------------------------------------------------------
            #      <template specializations for class Foo>
            class Foo_int:  # Python specialization for Foo<int>
                value: int
                def __init__(self, value: int = int()) -> None:
                    """Auto-generated default constructor with named params"""
                    pass
            #      </template specializations for class Foo>
            #  ------------------------------------------------------------------------

        # </submodule ns>
    ''',
    )


def test_inner_class() -> None:
    """
    When we have an inner enum, class or struct:
        1. We must place the pydef code of the inner struct *before* the pydef of the parent struct's children.
           Otherwise, the python module will fail to import: in the example below,
           "Choice" must be pydefined before the method "HandleChoice"
        2. Params that use the inner scope of the struct such as `Choice value = Choice::A`, which is in fact
           `Foo::Choice value = Foo::Choice::A` must be adjusted by adding the struct scope if necessary.
    """
    code = """
        struct Foo
        {
        public:
            enum class Choice {
                A = 0,
            };
            MY_API int HandleChoice(Choice value = Choice::A) { return 0; }
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
                (m, "Foo", "");

        { // inner classes & enums of Foo
            auto pyEnumChoice =
                py::enum_<Foo::Choice>(pyClassFoo, "Choice", py::arithmetic(), "")
                    .value("a", Foo::Choice::A, "");
        } // end of inner classes & enums of Foo

        pyClassFoo
            .def(py::init<>()) // implicit default constructor
            .def("handle_choice",
                &Foo::HandleChoice, py::arg("value") = Foo::Choice::A)
            ;
    """,
    )


def test_no_inner_class() -> None:
    code = """
        struct Foo
        {
        public:
            MY_API int HandleChoice(int value = 1) { return 0; }
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
            .def(py::init<>()) // implicit default constructor
            .def("handle_choice",
                &Foo::HandleChoice, py::arg("value") = 1)
            ;
    """,
    )


def test_named_ctor_helper_struct() -> None:
    code = """
    namespace A
    {
        enum class Foo
        {
            Foo1 = 0
        };
        struct ClassNoDefaultCtor
        {
            bool b = true;
            int a;
            int c = 3;
            Foo foo = Foo::Foo1;
            const std::string s = "Allo";
        };
    }
    """
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        # <submodule a>
        class a:  # Proxy class that introduces typings for the *submodule* a
            pass  # (This corresponds to a C++ namespace. All method are static!)
            class Foo(enum.Enum):
                foo1 = enum.auto() # (= 0)
            class ClassNoDefaultCtor:
                b: bool = True
                a: int
                c: int = 3
                foo: Foo = Foo.foo1
                s: str = "Allo" # (const)
                def __init__(
                    self,
                    b: bool = True,
                    a: int = int(),
                    c: int = 3,
                    foo: Foo = Foo.foo1
                    ) -> None:
                    """Auto-generated default constructor with named params"""
                    pass

        # </submodule a>
             ''',
    )

    # print(generated_code.pydef_code)

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        { // <namespace A>
            py::module_ pyNsA = m.def_submodule("a", "");
            auto pyEnumFoo =
                py::enum_<A::Foo>(pyNsA, "Foo", py::arithmetic(), "")
                    .value("foo1", A::Foo::Foo1, "");


            auto pyNsA_ClassClassNoDefaultCtor =
                py::class_<A::ClassNoDefaultCtor>
                    (pyNsA, "ClassNoDefaultCtor", "")
                .def(py::init<>([](
                bool b = true, int a = int(), int c = 3, A::Foo foo = A::Foo::Foo1)
                {
                    auto r = std::make_unique<A::ClassNoDefaultCtor>();
                    r->b = b;
                    r->a = a;
                    r->c = c;
                    r->foo = foo;
                    return r;
                })
                , py::arg("b") = true, py::arg("a") = int(), py::arg("c") = 3, py::arg("foo") = A::Foo::Foo1
                )
                .def_readwrite("b", &A::ClassNoDefaultCtor::b, "")
                .def_readwrite("a", &A::ClassNoDefaultCtor::a, "")
                .def_readwrite("c", &A::ClassNoDefaultCtor::c, "")
                .def_readwrite("foo", &A::ClassNoDefaultCtor::foo, "")
                .def_readonly("s", &A::ClassNoDefaultCtor::s, "")
                ;
        } // </namespace A>
    """,
    )


def test_named_ctor_helper_class() -> None:
    code = """
        class ClassNoDefaultCtor
        {
        public:
            bool b = true;
            int a;
            int c = 3;
            const std::string s = "Allo";
        };
    """
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class ClassNoDefaultCtor:
            b: bool = True
            a: int
            c: int = 3
            s: str = "Allo" # (const)
            def __init__(self) -> None:
                """Autogenerated default constructor"""
                pass
    ''',
    )

    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassClassNoDefaultCtor =
            py::class_<ClassNoDefaultCtor>
                (m, "ClassNoDefaultCtor", "")
            .def(py::init<>()) // implicit default constructor
            .def_readwrite("b", &ClassNoDefaultCtor::b, "")
            .def_readwrite("a", &ClassNoDefaultCtor::a, "")
            .def_readwrite("c", &ClassNoDefaultCtor::c, "")
            .def_readonly("s", &ClassNoDefaultCtor::s, "")
            ;
        """,
    )


def test_shared_holder():
    code = "struct Foo {};"
    options = litgen.LitgenOptions()
    options.class_held_as_shared__regex = r"Foo"
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo, std::shared_ptr<Foo>>
                (m, "Foo", "")
            .def(py::init<>()) // implicit default constructor
            ;
    """,
    )


def test_ctor_placement_new():
    # Test placement new for constructors (required for nanobind)
    code = """
        struct Foo
        {
            int x = 1;
        };
    """
    options = litgen.LitgenOptions()

    # Test with pybind11: the ctor will use a lambda
    options.bind_library = litgen.BindLibraryType.pybind11
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            py::class_<Foo>
                (m, "Foo", "")
            .def(py::init<>([](
            int x = 1)
            {
                auto r = std::make_unique<Foo>();
                r->x = x;
                return r;
            })
            , py::arg("x") = 1
            )
            .def_readwrite("x", &Foo::x, "")
            ;
    """,
    )

    # Test with nanobind: the ctor shall use placement new
    options.bind_library = litgen.BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassFoo =
            nb::class_<Foo>
                (m, "Foo", "")
            .def("__init__", [](Foo * self, int x = 1)
            {
                new (self) Foo();  // placement new
                auto r = self;
                r->x = x;
            },
            nb::arg("x") = 1
            )
            .def_rw("x", &Foo::x, "")
            ;
        """,
    )


def test_numeric_array_member() -> None:
    # Test that a numeric array member is correctly exposed as a numpy array
    code = """
        struct Color4
        {
            uint8_t rgba[4];
        };
    """
    options = litgen.LitgenOptions()

    # Test with pybind11
    options.bind_library = litgen.BindLibraryType.pybind11
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassColor4 =
            py::class_<Color4>
                (m, "Color4", "")
            .def(py::init<>()) // implicit default constructor
            .def_property("rgba",
                [](Color4 &self) -> pybind11::array
                {
                    auto dtype = pybind11::dtype(pybind11::format_descriptor<uint8_t>::format());
                    auto base = pybind11::array(dtype, {4}, {sizeof(uint8_t)});
                    return pybind11::array(dtype, {4}, {sizeof(uint8_t)}, self.rgba, base);
                }, [](Color4& self) {},
                "")
            ;
    """,
    )

    # Test with nanobind
    options.bind_library = litgen.BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassColor4 =
            nb::class_<Color4>
                (m, "Color4", "")
            .def(nb::init<>()) // implicit default constructor
            .def_prop_ro("rgba",
                [](Color4 &self) -> nb::ndarray<uint8_t, nb::numpy, nb::shape<4>, nb::c_contig>
                {
                    return self.rgba;
                },
                "")
            ;
    """,
    )


def test_nanobind_adapted_ctor_stub() -> None:
    # The constructor params below will automatically be "adapted" into std::array<uint8_t, 4>
    code = """
    struct Color4
    {
        Color4(const uint8_t _rgba[4]);
        uint8_t rgba[4];
    };
    """
    options = litgen.LitgenOptions()
    options.bind_library = BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)

    # Below, we test that the ctor signature is adapted to accept List[int]
    # (and does not specify an additional self parameter, cf AdaptedFunction.stub_params_list_signature())
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class Color4:
            def __init__(self, _rgba: List[int]) -> None:
                pass
            rgba: np.ndarray  # ndarray[type=uint8_t, size=4]
        """,
    )


def test_adapted_ctor() -> None:
    # The constructor for Color4 will be adapted to accept std::array<uint8_t, 4>
    code = """
        struct Color4
        {
            Color4(const uint8_t _rgba[4]) {}
        };
    """
    options = litgen.LitgenOptions()

    #
    # Test with pybind11 (using lambda & unique_ptr)
    #
    options.bind_library = BindLibraryType.pybind11
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassColor4 =
            py::class_<Color4>
                (m, "Color4", "")
            .def(py::init(
                [](const std::array<uint8_t, 4>& _rgba) -> std::unique_ptr<Color4>
                {
                    auto ctor_wrapper = [](const uint8_t _rgba[4]) ->  std::unique_ptr<Color4>
                    {
                        return std::make_unique<Color4>(_rgba);
                    };
                    auto ctor_wrapper_adapt_fixed_size_c_arrays = [&ctor_wrapper](const std::array<uint8_t, 4>& _rgba) -> std::unique_ptr<Color4>
                    {
                        auto lambda_result = ctor_wrapper(_rgba.data());
                        return lambda_result;
                    };

                    return ctor_wrapper_adapt_fixed_size_c_arrays(_rgba);
                }),     py::arg("_rgba"))
            ;
        """,
    )

    #
    # Test with nanobind (using placement new)
    #
    options.bind_library = BindLibraryType.nanobind
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.pydef_code)
    code_utils.assert_are_codes_equal(
        generated_code.pydef_code,
        """
        auto pyClassColor4 =
            nb::class_<Color4>
                (m, "Color4", "")
            .def("__init__",
                [](Color4 * self, const std::array<uint8_t, 4>& _rgba)
                {
                    auto ctor_wrapper = [](Color4* self, const uint8_t _rgba[4]) ->  void
                    {
                        new(self) Color4(_rgba); // placement new
                    };
                    auto ctor_wrapper_adapt_fixed_size_c_arrays = [&ctor_wrapper](Color4 * self, const std::array<uint8_t, 4>& _rgba)
                    {
                        ctor_wrapper(self, _rgba.data());
                    };

                    ctor_wrapper_adapt_fixed_size_c_arrays(self, _rgba);
                },     nb::arg("_rgba"))
            ;
        """,
    )


def test_named_ctor_with_optional() -> None:
    code = """
    struct Inner {};

    struct Foo {
        MyVector<Inner> inner;
    };
    """
    options = litgen.LitgenOptions()
    options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Inner:
            def __init__(self) -> None:
                """Auto-generated default constructor"""
                pass

        class Foo:
            inner: MyVector[Inner]
            def __init__(self, inner: Optional[MyVector[Inner]] = None) -> None:
                """Auto-generated default constructor with named params
                ---
                Python bindings defaults:
                    If inner is None, then its default value will be: MyVector<Inner>()
                """
                pass
        '''
    )


def test_instantiated_template() -> None:
    code = """
    template<typename T> struct ImVector {
        ImVector();
        T value(size_t i);
    };
    struct Foo {
        ImVector<int> values;
    };
    """
    options = litgen.LitgenOptions()
    options.class_template_options.add_specialization("ImVector", ["int"], None)
    _generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    # TODO: stub_code contains ImVector[int] instead of ImVector_int
    #     class Foo:
    #         values: ImVector_int
    #         def __init__(self, values: Optional[ImVector[int]] = None) -> None:
