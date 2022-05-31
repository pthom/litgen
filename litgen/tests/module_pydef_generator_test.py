import logging
import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

from litgen.internal import module_pydef_generator, code_utils
from litgen.internal import srcml
from litgen import CodeStyleOptions, code_style_implot, code_style_immvision


def test_generate_pydef_enum():
    options = code_style_implot()

    code1 = """
        // This is the enum doc
        enum MyEnum {
            // A doc on several values 
            MyEnum_A = 0, // Doc about A
            MyEnum_B,     // Doc about B
            // Count the number of values in the enum
            MyEnum_COUNT
        };        
    """

    expected_generated_code1 = """
        py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(),
            "This is the enum doc")
            // A doc on several values
            .value("a", MyEnum_A, "(Doc about A)")
            .value("b", MyEnum_B, "(Doc about B)")
        ;
    """

    cpp_unit1 = srcml.code_to_cpp_unit(options, code1)
    generated_code1 = module_pydef_generator.generate_pydef(cpp_unit1, options)
    code_utils.assert_are_codes_equal(expected_generated_code1, generated_code1)

    code2 = """
        // This is the enum doc
        enum class MyEnum {
            // A doc on several values
            A = 0, // Doc about A
            B,     // Doc about B
            // Count the number of values in the enum
            COUNT
        };
    """
    expected_generated_code2 = """
        py::enum_<MyEnum>(m, "MyEnum", py::arithmetic(),
            "This is the enum doc")
            // A doc on several values
            .value("a", MyEnum::A, "(Doc about A)")
            .value("b", MyEnum::B, "(Doc about B)")
        ;
    """
    cpp_unit2 = srcml.code_to_cpp_unit(options, code2)
    generated_code2 = module_pydef_generator.generate_pydef(cpp_unit2, options)
    code_utils.assert_are_codes_equal(expected_generated_code2, generated_code2)
