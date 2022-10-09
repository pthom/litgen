from srcmlcpp.srcml_types import *

import litgen
from litgen.options import LitgenOptions
from litgen.litgen_generator import LitgenGeneratorTestsHelper


def log_code(code: str) -> None:
    logging.warning(f"\n>>>{code}<<<")


def test_struct_stub_layouts():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}

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
    ''',
    )


def test_struct_pydef_simple():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}
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
            .def(py::init<>()) // implicit default constructor
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
    options.srcml_options.functions_api_prefixes = "MY_API"
    options.fn_params_replace_modifiable_immutable_by_boxed__regex
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
                        auto r = ctor_wrapper(values.data());
                        return r;
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
        class_name_regex="^MyTemplateClass",
        cpp_types_list=["std::string"],
        naming_scheme=litgen.TemplateNamingScheme.camel_case_suffix,
    )

    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        #  ------------------------------------------------------------------------
        #      <template specializations for class MyTemplateClass>
        class MyTemplateClassString:
            values: List[str]

            def __init__(self) -> None:
                """ Standard constructor"""
                pass

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
                (m, "MyTemplateClassString", "")
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
                        auto r = ctor_wrapper(v.data());
                        return r;
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
                        auto r = self.sum2(v.data());
                        return r;
                    };

                    return sum2_adapt_fixed_size_c_arrays(v);
                },
                py::arg("v"),
                "Method that requires a parameter adaptation")
            ;
    """,
    )
