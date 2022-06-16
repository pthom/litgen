import os

import litgen.internal.module_pydef_generator
from litgen import CodeStyleOptions
from litgen.internal import code_utils, module_pydef_generator, module_pyi_generator
import srcmlcpp


def generate_pydef(
    code: str,
    options: CodeStyleOptions,
    add_boxed_types_definitions: bool = False,
    filename: str = "",
) -> str:

    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code, filename=filename)
    generated_code = module_pydef_generator.generate_pydef(
        cpp_unit, options, add_boxed_types_definitions=add_boxed_types_definitions
    )
    return generated_code


def generate_pyi(
    code: str,
    options: CodeStyleOptions,
    add_boxed_types_definitions: bool = False,
    filename: str = "",
) -> str:
    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code, filename=filename)
    generated_code = module_pyi_generator.generate_pyi(
        cpp_unit, options, add_boxed_types_definitions=add_boxed_types_definitions
    )
    return generated_code


def _run_generate_file(
    input_cpp_header: str,
    output_file: str,
    fn_code_generator,
    marker_token: str,
    options: CodeStyleOptions,
    add_boxed_types_definitions: bool,
):
    assert os.path.isfile(input_cpp_header)
    assert os.path.isfile(output_file)

    options.assert_buffer_types_are_ok()

    header_code = code_utils.read_text_file(input_cpp_header)

    generated_code = fn_code_generator(header_code, options, add_boxed_types_definitions, filename=input_cpp_header)

    marker_in = f"<autogen:{marker_token}>"
    marker_out = f"</autogen:{marker_token}>"

    code_utils.write_code_between_markers(output_file, marker_in, marker_out, generated_code)


def generate_files(
    input_cpp_header: str,
    output_cpp_module_file: str,
    options: CodeStyleOptions,
    output_stub_pyi_file: str = "",
    add_boxed_types_definitions: bool = True,
):

    # _run_generate_file(input_cpp_header,
    #                    output_cpp_module_file,
    #                    generate_pydef,
    #                    "pydef_cpp",
    #                    options,
    #                    add_boxed_types_definitions)

    _run_generate_file(
        input_cpp_header,
        output_stub_pyi_file,
        generate_pyi,
        "pyi",
        options,
        add_boxed_types_definitions,
    )
