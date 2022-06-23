from typing import Optional
from dataclasses import dataclass
import logging

from codemanip import code_utils

from litgen.options import LitgenOptions
from litgen.internal import boxed_immutable_python_type, cpp_to_python
from litgen._generated_code import GeneratedCode
from litgen.internal.adapted_types.adapted_block import AdaptedUnit
from litgen.code_to_adapted_unit import code_to_adapted_unit


def generate_code(
    options: LitgenOptions,
    code: str = "",
    filename: str = "",
    add_boxed_types_definitions: bool = False,
) -> GeneratedCode:

    boxed_immutable_python_type.clear_registry()

    adapted_unit = code_to_adapted_unit(options, code, filename)

    generated_code = GeneratedCode()
    generated_code.cpp_header_code = code
    generated_code.pydef_code = adapted_unit.str_pydef()
    generated_code.stub_code = adapted_unit.str_stub()

    generated_code.boxed_types_generated_code = boxed_immutable_python_type.all_boxed_types_generated_code(options)

    if add_boxed_types_definitions:
        if generated_code.boxed_types_generated_code is None:
            logging.warning(f"generate_code: no boxed types definition required.")
        else:
            generated_code.stub_code = (
                generated_code.boxed_types_generated_code.stub_code + "\n\n" + generated_code.stub_code
            )
            generated_code.pydef_code = (
                generated_code.boxed_types_generated_code.pydef_code + "\n\n" + generated_code.pydef_code
            )

    # Apply Python code layout options
    generated_code.stub_code = code_utils.code_set_max_consecutive_empty_lines(
        generated_code.stub_code, options.python_max_consecutive_empty_lines
    )
    generated_code.stub_code = cpp_to_python.apply_black_formatter_pyi(options, generated_code.stub_code)

    return generated_code


def code_to_pydef(
    options: LitgenOptions, code: str, filename: str = "", add_boxed_types_definitions: bool = False
) -> str:
    generated_code = generate_code(options, code, filename, add_boxed_types_definitions)
    return generated_code.pydef_code


def code_to_stub(
    options: LitgenOptions, code: str, filename: str = "", add_boxed_types_definitions: bool = False
) -> str:
    generated_code = generate_code(options, code, filename, add_boxed_types_definitions)
    return generated_code.stub_code


def write_generated_code(
    options: LitgenOptions,
    input_cpp_header: str,
    output_cpp_pydef_file: str = "",
    output_stub_pyi_file: str = "",
    output_boxed_types_header_file: str = "",
    add_boxed_types_definitions: bool = True,
) -> None:

    if add_boxed_types_definitions:
        if len(output_boxed_types_header_file) == 0:
            raise ValueError(
                f"write_generated_code: specify output_boxed_types_header_file if add_boxed_types_definitions=True"
            )

    generated_code = generate_code(
        options, filename=input_cpp_header, add_boxed_types_definitions=add_boxed_types_definitions
    )

    if len(output_cpp_pydef_file) > 0:
        code_utils.write_generated_code_between_markers(output_cpp_pydef_file, "pydef", generated_code.pydef_code)
    if len(output_stub_pyi_file) > 0:
        code_utils.write_generated_code_between_markers(output_stub_pyi_file, "stub", generated_code.stub_code)
    if len(output_boxed_types_header_file) > 0 and generated_code.boxed_types_generated_code is not None:
        code_utils.write_generated_code_between_markers(
            output_boxed_types_header_file,
            "boxed_types_header",
            generated_code.boxed_types_generated_code.cpp_header_code,
        )
