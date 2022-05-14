import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import code_utils
from code_types import *
from options import CodeStyleOptions, code_style_immvision, code_style_implot
import struct_generator, struct_parser


OPTIONS = code_style_implot()


SIMPLE_STRUCT = """
    // A dummy structure that likes to multiply
    struct Multiplier 
    { 
        // Doubles the input number
        int CalculateDouble(int x = 21) 
        { 
            return x * 2; 
        }
        // Who is who?
        int who = 627;
    };
    """


# def test_make_struct_doc():
#     struct_infos = struct_parser.parse_one_struct_testonly(SIMPLE_STRUCT, OPTIONS)
#     doc = struct_generator.make_struct_doc(struct_infos, OPTIONS)
#     print(doc)
#     assert False


# def test_generate_pyi_python_code():
#     struct_infos = struct_parser.parse_one_struct_testonly(SIMPLE_STRUCT, OPTIONS)
#     doc = struct_generator.generate_pyi_python_code(struct_infos, OPTIONS)
#     print(doc)
#     assert False


def test_generate_pydef_struct_cpp_code():
    struct_infos = struct_parser.parse_one_struct_testonly(SIMPLE_STRUCT, OPTIONS)
    code = struct_generator.generate_pydef_struct_cpp_code(struct_infos, OPTIONS)
    expected_code = """
        auto pyClassMultiplier = py::class_<Multiplier>
            (m, "Multiplier",
            "A dummy structure that likes to multiply")
        
            .def(py::init<>())
        
            .def("calculate_double",
                [](Multiplier& self, int x = 21)
                {
                    { return self.CalculateDouble(x); }
                },
                py::arg("x") = 21,
                "Doubles the input number"
            )
        
            .def_readwrite("who", &Multiplier::who, "Who is who?")
            ;
    """
    code_utils.assert_are_codes_equal(code, expected_code)
