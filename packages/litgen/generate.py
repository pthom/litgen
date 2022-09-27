from typing import Optional, List

from codemanip import code_utils

from litgen.internal import boxed_python_type, cpp_to_python
from litgen._generated_code import GeneratedCodeForOneFile, GeneratedCode, CppFile
from litgen.code_to_adapted_unit import code_to_adapted_unit
from litgen.litgen_context import LitgenContext


def _generate_code_impl_one_file(cpp_file: CppFile, lg_context: LitgenContext) -> GeneratedCodeForOneFile:
    adapted_unit = code_to_adapted_unit(
        lg_context,
        cpp_file.code,
        cpp_file.filename,
    )
    filename = cpp_file.filename if cpp_file.filename is not None else ""
    generated_code = GeneratedCodeForOneFile(filename)
    generated_code.pydef_code = adapted_unit.str_pydef()
    generated_code.stub_code = adapted_unit.str_stub()

    # Apply Python code layout options
    options = lg_context.options
    generated_code.stub_code = code_utils.code_set_max_consecutive_empty_lines(
        generated_code.stub_code, options.python_max_consecutive_empty_lines
    )
    generated_code.stub_code = cpp_to_python.apply_black_formatter_pyi(options, generated_code.stub_code)

    return generated_code


def merge_generated_codes(
    generated_codes: List[GeneratedCodeForOneFile],
    lg_context: LitgenContext,
    add_boxed_types_definitions: bool = False,
) -> GeneratedCode:

    boxed_types_generated_code = boxed_python_type.generated_code_for_registered_boxed_types(lg_context)
    generated_code = GeneratedCode(
        generated_codes, boxed_types_generated_code, add_boxed_types_definitions, lg_context.options
    )
    return generated_code


def generate_code_for_files(
    lg_context: LitgenContext, file_list: List[CppFile], add_boxed_types_definitions: bool = False
) -> GeneratedCode:

    assert len(file_list) > 0

    generated_codes: List[GeneratedCodeForOneFile] = []
    for file in file_list:
        file_generated_code = _generate_code_impl_one_file(file, lg_context)
        generated_codes.append(file_generated_code)

    generated_code = merge_generated_codes(generated_codes, lg_context, add_boxed_types_definitions)

    return generated_code


def generate_code(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> GeneratedCode:

    cpp_files_list = [CppFile(lg_context.options, filename, code)]
    generated_code = generate_code_for_files(lg_context, cpp_files_list, add_boxed_types_definitions)
    return generated_code


def code_to_pydef(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    file_and_options_list = [CppFile(lg_context.options, filename, code)]
    generated_code = generate_code_for_files(lg_context, file_and_options_list, add_boxed_types_definitions)
    return generated_code.pydef_code


def code_to_stub(
    lg_context: LitgenContext,
    code: Optional[str] = None,
    filename: Optional[str] = None,
    add_boxed_types_definitions: bool = False,
) -> str:
    files_list = [CppFile(lg_context.options, filename, code)]
    generated_code = generate_code_for_files(lg_context, files_list, add_boxed_types_definitions)
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
