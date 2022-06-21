from srcmlcpp import srcml_main
from srcmlcpp.srcml_types import *

import litgen
from litgen.internal.adapted_types import *
from litgen.options import code_style_immvision


def test_adapted_struct():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}

    code = """
// Doc about Foo
struct Foo
{
    int a;
    int add(int v) { return v + a; }
};
    """
    pydef_code = litgen.code_to_pydef(options, code)
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyClassFoo = py::class_<Foo>
            (m, "Foo", "Doc about Foo")
            .def(py::init<>()) // implicit default constructor
            .def_readwrite("a", &Foo::a, "")
            .def("add",
                [](Foo & self, int v)
                {
                    return self.add(v);
                },
                py::arg("v")
            )
            ;
    """,
    )


def test_generate_pydef_struct_cpp_code():
    options = code_style_immvision()
    code = """
        // A dummy structure that likes to multiply
        struct Multiplier
        {
            Multiplier(); // default constructor

            // Constructor with param
            Multiplier(int _who): who(_who) {};

            // Doubles the input number
            IMMVISION_API int CalculateDouble(int x = 21)
            {
                return x * 2;
            }
            // Who is who?
            int who = 627;
        };
    """
    generated = litgen.code_to_pydef(options, code)
    expected_code = """
        auto pyClassMultiplier = py::class_<Multiplier>
            (m, "Multiplier", "A dummy structure that likes to multiply")
            .def(py::init<>(),
                "default constructor")
            .def(py::init<int>(),
                py::arg("_who"),
                "Constructor with param")
            .def("calculate_double",
                [](Multiplier & self, int x = 21)
                {
                    return self.CalculateDouble(x);
                },
                py::arg("x") = 21,
                "Doubles the input number"
            )
            .def_readwrite("who", &Multiplier::who, "Who is who?")
            .def("__repr__", [](const Multiplier& v) { return ToString(v); });
    """
    # logging.warning("\n" + generated)
    code_utils.assert_are_codes_equal(generated, expected_code)
