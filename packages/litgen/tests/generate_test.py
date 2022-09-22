import litgen
import os


_THIS_DIR = os.path.dirname(__file__)
_TEST_EXAMPLES_DIR = os.path.realpath(_THIS_DIR + "/../test_examples")


def _run_test_impl(test_name: str) -> None:
    folder = f"{_TEST_EXAMPLES_DIR}/{test_name}"
    assert os.path.isdir(folder)
    out_folder = folder + "/computed"

    input_cpp_header = f"{folder}/{test_name}.h"
    output_cpp_pydef_file = f"{out_folder}/pybind_{test_name}.cpp"
    output_stub_pyi_file = f"{out_folder}/stubs/{test_name}.pyi"
    output_boxed_types_header_file = f"{out_folder}/{test_name}_boxed_types.h"

    # Configure options
    options = litgen.LitgenOptions()
    generated_code = litgen.generate_code(options, filename=input_cpp_header, add_boxed_types_definitions=True)
    litgen.write_generated_code(
        generated_code,
        output_cpp_pydef_file=output_cpp_pydef_file,
        output_stub_pyi_file=output_stub_pyi_file,
        output_boxed_types_header_file=output_boxed_types_header_file,
    )
    print(generated_code.boxed_types_cpp_declaration)


# def test_basic():
#     _run_test_impl("basic")


def test_inner_classes():
    from litgen.tests import boxed_immutable_python_type_test

    boxed_immutable_python_type_test.test_make_boxed_type()
    _run_test_impl("inner_classes")


# def test_subclass():
#     code = """
#     struct Parent
#     {
#         int a;
#         struct Child
#         {
#             int b;
#         };
#         Child child;
#
#         /*
#         enum class ChildEnum
#         {
#             one = 1, two, three;
#         };
#
#         ChildEnum child_enum = ChildEnum::three;
#         */
#     };
#     """
#     from litgen import code_to_adapted_unit
#
#     # Configure options
#     options = litgen.LitgenOptions()
#     pydef_code = litgen.code_to_pydef(options, code)
#     print("\n" + pydef_code)
#
#     stub_code = litgen.code_to_stub(options, code)
#     print("\n" + stub_code)
