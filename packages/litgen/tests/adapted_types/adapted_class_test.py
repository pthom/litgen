from srcmlcpp.srcml_types import *

import litgen
from litgen.options import LitgenOptions


def log_code(code) -> None:
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
    stub_code = litgen.code_to_stub(options, code)
    # log_code(stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo:
            """ Doc about Foo"""
            # Doc about members
            a:int      # Doc about a
            flag:bool  # Doc about flag


            # Doc about Methods
            def add(self, v: int) -> int:
                """ Simple addition"""
                pass
    ''',
    )

    options.python_reproduce_cpp_layout = False
    stub_code = litgen.code_to_stub(options, code)
    # log_code(stub_code)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo:
            """ Doc about Foo"""

            # Doc about members

            # Doc about a
            a:int
            # Doc about flag
            flag:bool

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

    pydef_code = litgen.code_to_pydef(options, code)
    # log_code(pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassFoo = py::class_<Foo>
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
    options.srcml_options.functions_api_prefixes = ["MY_API"]
    options.srcml_options.api_suffixes = ["MY_API"]
    code = """
        // A dummy class that handles 4 channel float colors
        class Color4 // MY_API
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
    stub_code = litgen.code_to_stub(options, code)
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
            flag_bgra:bool = False  # True if color order is BGRA
            components:np.ndarray   # ndarray[type=float, size=4]  # A numeric C array that will be published as a numpy array
    ''',
    )

    pydef_code = litgen.code_to_pydef(options, code)
    # log_code(pydef_code)
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassColor4 = py::class_<Color4>
            (m, "Color4", "A dummy class that handles 4 channel float colors")
            .def(py::init<const float>(),
                py::arg("values"))
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
