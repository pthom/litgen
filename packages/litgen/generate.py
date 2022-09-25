from typing import Optional, List

from codemanip import code_utils

from litgen.options import LitgenOptions
from litgen.internal import boxed_python_type, cpp_to_python
from litgen._generated_code import GeneratedCodeForOneFile, GeneratedCode, CppFile
from litgen.code_to_adapted_unit import code_to_adapted_unit
from litgen.internal.adapted_types.litgen_writer_context import LitgenWriterContext


def _generate_code_impl_one_file(cpp_file: CppFile, lg_writer_context: LitgenWriterContext) -> GeneratedCodeForOneFile:

    adapted_unit = code_to_adapted_unit(
        lg_writer_context,
        cpp_file.code,
        cpp_file.filename,
    )

    generated_code = GeneratedCodeForOneFile()
    generated_code.pydef_code = adapted_unit.str_pydef()
    generated_code.stub_code = adapted_unit.str_stub()
    generated_code.translated_cpp_filename = cpp_file.filename

    # Apply Python code layout options
    options = lg_writer_context.options
    generated_code.stub_code = code_utils.code_set_max_consecutive_empty_lines(
        generated_code.stub_code, options.python_max_consecutive_empty_lines
    )
    generated_code.stub_code = cpp_to_python.apply_black_formatter_pyi(options, generated_code.stub_code)

    return generated_code


def generate_code_for_files(
    options: LitgenOptions, file_list: List[CppFile], add_boxed_types_definitions: bool = False
) -> GeneratedCode:

    assert len(file_list) > 0

    lg_writer_context = LitgenWriterContext(options)

    generated_codes: List[GeneratedCodeForOneFile] = []
    for file in file_list:
        file_generated_code = _generate_code_impl_one_file(file, lg_writer_context)
        generated_codes.append(file_generated_code)

    boxed_types_generated_code = boxed_python_type.generated_code_for_registered_boxed_types(lg_writer_context)
    generated_code = GeneratedCode(generated_codes, boxed_types_generated_code, add_boxed_types_definitions, options)

    return generated_code


def generate_code(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> GeneratedCode:

    cpp_files_list = [CppFile(options, filename, code)]

    generated_code = generate_code_for_files(options, cpp_files_list, add_boxed_types_definitions)
    return generated_code


def code_to_pydef(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    file_and_options_list = [CppFile(options, filename, code)]
    generated_code = generate_code_for_files(options, file_and_options_list, add_boxed_types_definitions)
    return generated_code.pydef_code


def code_to_stub(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    files_list = [CppFile(options, filename, code)]
    generated_code = generate_code_for_files(options, files_list, add_boxed_types_definitions)
    return generated_code.stub_code


def write_generated_code(
    generated_code: GeneratedCode,
    output_cpp_pydef_file: str = "",
    output_stub_pyi_file: str = "",
    output_boxed_types_header_file: str = "",
) -> None:

    if generated_code.boxed_types_cpp_declaration is not None and len(output_boxed_types_header_file) == 0:
        raise ValueError("write_generated_code: specify output_boxed_types_header_file")

    if len(output_cpp_pydef_file) > 0:
        code_utils.write_generated_code_between_markers(output_cpp_pydef_file, "pydef", generated_code.pydef_code)
    if len(output_stub_pyi_file) > 0:
        code_utils.write_generated_code_between_markers(output_stub_pyi_file, "stub", generated_code.stub_code)

    if len(output_boxed_types_header_file) > 0 and generated_code.boxed_types_cpp_declaration is not None:
        code_utils.write_generated_code_between_markers(
            output_boxed_types_header_file,
            "boxed_types_header",
            generated_code.boxed_types_cpp_declaration,
        )
