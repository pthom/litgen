from typing import Optional, List

from codemanip import code_utils

from litgen.options import LitgenOptions
from litgen.internal import boxed_immutable_python_type, cpp_to_python
from litgen._generated_code import (
    GeneratedCodeForOneFile,
    GeneratedCode,
    CppFileAndOptions,
    CppFilesAndOptionsList,
)
from litgen.code_to_adapted_unit import code_to_adapted_unit


def _generate_code_impl_one_file(cpp_file_and_options: CppFileAndOptions) -> GeneratedCodeForOneFile:

    adapted_unit = code_to_adapted_unit(
        cpp_file_and_options.options, cpp_file_and_options.code, cpp_file_and_options.filename
    )

    generated_code = GeneratedCodeForOneFile()
    generated_code.pydef_code = adapted_unit.str_pydef()
    generated_code.stub_code = adapted_unit.str_stub()
    generated_code.translated_cpp_filename = cpp_file_and_options.filename

    return generated_code


def generate_code_for_files(
    files_and_options: CppFilesAndOptionsList, add_boxed_types_definitions: bool = False
) -> GeneratedCode:

    assert len(files_and_options.files_and_options) > 0
    boxed_immutable_python_type.clear_registry()

    generated_codes: List[GeneratedCodeForOneFile] = []
    for file in files_and_options.files_and_options:
        file_generated_code = _generate_code_impl_one_file(file)
        generated_codes.append(file_generated_code)

    first_options = files_and_options.files_and_options[0].options
    boxed_types_generated_code = boxed_immutable_python_type.all_boxed_types_generated_code(first_options)

    generated_code = GeneratedCode(
        generated_codes, boxed_types_generated_code, add_boxed_types_definitions, first_options
    )

    # Apply Python code layout options
    generated_code.stub_code = code_utils.code_set_max_consecutive_empty_lines(
        generated_code.stub_code, first_options.python_max_consecutive_empty_lines
    )
    generated_code.stub_code = cpp_to_python.apply_black_formatter_pyi(first_options, generated_code.stub_code)

    return generated_code


def generate_code(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> GeneratedCode:

    cpp_file_and_options = CppFileAndOptions(options, filename, code)
    cpp_files_and_options_list = CppFilesAndOptionsList([cpp_file_and_options])

    generated_code = generate_code_for_files(cpp_files_and_options_list, add_boxed_types_definitions)
    return generated_code


def code_to_pydef(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    file_and_options = CppFileAndOptions(options, filename, code)
    file_and_options_list = CppFilesAndOptionsList([file_and_options])
    generated_code = generate_code_for_files(file_and_options_list, add_boxed_types_definitions)
    return generated_code.pydef_code


def code_to_stub(
    options: LitgenOptions,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    file_and_options = CppFileAndOptions(options, filename, code)
    file_and_options_list = CppFilesAndOptionsList([file_and_options])
    generated_code = generate_code_for_files(file_and_options_list, add_boxed_types_definitions)
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
