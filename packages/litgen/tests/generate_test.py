import litgen
import os
from dataclasses import dataclass


_THIS_DIR = os.path.dirname(__file__)
_TEST_EXAMPLES_DIR = os.path.realpath(_THIS_DIR + "/../test_examples")


def test_basic():
    test_name = "basic"
    folder = f"{_TEST_EXAMPLES_DIR}/{test_name}"
    assert os.path.isdir(folder)
    out_folder = folder + "/computed"

    input_cpp_header = f"{folder}/{test_name}.h"
    output_cpp_pydef_file = f"{out_folder}/pybind_{test_name}.cpp"
    output_stub_pyi_file = f"{out_folder}/stubs/{test_name}.pyi"

    # Configure options
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, filename=input_cpp_header)
    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
    )

    print(generated_code.pydef_code)
