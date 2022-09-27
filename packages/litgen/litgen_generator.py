from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Optional

from codemanip import code_utils

from litgen import LitgenContext, LitgenOptions
from litgen.code_to_adapted_unit import code_to_adapted_unit
from litgen.internal import cpp_to_python
from litgen.internal import boxed_python_type2

CppFilename = str
CppCode = str
PythonCode = str


@dataclass
class GeneratedCode:
    source_filename: CppFilename
    pydef_code: CppCode
    stub_code: PythonCode


class LitgenGenerator:
    lg_context: LitgenContext
    _generated_codes: List[GeneratedCode]

    def __init__(self, options: LitgenOptions) -> None:
        self.lg_context = LitgenContext(options)
        self._generated_codes = []

    def options(self) -> LitgenOptions:
        return self.lg_context.options

    def _process_cpp_code(self, code: str, filename: str) -> None:
        adapted_unit = code_to_adapted_unit(self.lg_context, code)
        stub_code = adapted_unit.str_stub()
        pydef_code = adapted_unit.str_pydef()
        generated_code = GeneratedCode(source_filename=filename, stub_code=stub_code, pydef_code=pydef_code)
        self._generated_codes.append(generated_code)

    def process_cpp_file(self, filename: str) -> None:
        code = _read_code(self.lg_context.options, filename)
        self._process_cpp_code(code, filename)

    def has_boxed_types(self) -> bool:
        return len(self.lg_context.boxed_types_registry.cpp_boxed_types) > 0

    def _boxed_types_cpp_code(self) -> CppCode:
        cpp_codes = []
        for cpp_boxed_type in self.lg_context.boxed_types_registry.cpp_boxed_types:
            indent_str = self.lg_context.options.indent_cpp_spaces()
            cpp_codes.append(boxed_python_type2.boxed_type_cpp_struct_code(cpp_boxed_type, indent_str))
        r = "".join(cpp_codes)
        return r

    def _boxed_types_generated_code(self) -> Optional[GeneratedCode]:
        boxed_types_cpp_code = self._boxed_types_cpp_code()

        standalone_options = LitgenOptions()
        standalone_options.cpp_indent_size = self.options().cpp_indent_size
        standalone_options.cpp_indent_with_tabs = self.options().cpp_indent_with_tabs

        adapted_unit = code_to_adapted_unit(LitgenContext(standalone_options), boxed_types_cpp_code)

        stub_code = adapted_unit.str_stub()
        pydef_code = adapted_unit.str_pydef()
        generated_code = GeneratedCode("BoxedTypes", stub_code=stub_code, pydef_code=pydef_code)
        return generated_code

    def _generated_codes_with_boxed_types(self) -> List[GeneratedCode]:
        boxed_types_generated_code = self._boxed_types_generated_code()
        if boxed_types_generated_code is None:
            return self._generated_codes
        else:
            r = [boxed_types_generated_code] + self._generated_codes
            return r

    def _pydef_code(self) -> str:
        pydef_codes = []
        for generated_code in self._generated_codes_with_boxed_types():
            decorated_pydef_code = cpp_to_python.surround_cpp_code_with_filename(
                self.lg_context.options, generated_code.source_filename, generated_code.pydef_code
            )
            pydef_codes.append(decorated_pydef_code)
        pydef_code = "\n\n".join(pydef_codes)
        return pydef_code

    def _stub_code(self) -> str:
        stub_codes = []
        for generated_code in self._generated_codes_with_boxed_types():
            decorated_stub_code = cpp_to_python.surround_python_code_with_filename(
                self.lg_context.options, generated_code.source_filename, generated_code.stub_code
            )
            stub_codes.append(decorated_stub_code)
        stub_code = "\n\n".join(stub_codes)
        return stub_code

    def write_generated_code(self, output_cpp_pydef_file: str, output_stub_pyi_file: str) -> None:

        pydef_code = self._pydef_code()
        stub_code = self._stub_code()
        code_utils.write_generated_code_between_markers(output_cpp_pydef_file, "pydef", pydef_code)
        code_utils.write_generated_code_between_markers(output_stub_pyi_file, "stub", stub_code)

        if self.has_boxed_types():
            boxed_types_cpp_code = self._boxed_types_cpp_code()
            code_utils.write_generated_code_between_markers(
                output_cpp_pydef_file, "boxed_types_header", boxed_types_cpp_code
            )


def write_generated_code_for_files(
    options: LitgenOptions,
    input_cpp_header_files: List[str],
    output_cpp_pydef_file: str = "",
    output_stub_pyi_file: str = "",
) -> None:

    generator = LitgenGenerator(options)
    for cpp_header in input_cpp_header_files:
        generator.process_cpp_file(cpp_header)
    generator.write_generated_code(output_cpp_pydef_file, output_stub_pyi_file)


def write_generated_code_for_file(
    options: LitgenOptions, input_cpp_header_file: str, output_cpp_pydef_file: str = "", output_stub_pyi_file: str = ""
) -> None:
    return write_generated_code_for_files(options, [input_cpp_header_file], output_cpp_pydef_file, output_stub_pyi_file)


class LitgenGeneratorTestUtils:
    @staticmethod
    def code_to_pydef(options: LitgenOptions, code: str) -> str:
        generator = LitgenGenerator(options)
        generator._process_cpp_code(code, "")
        r = generator._pydef_code()
        return r

    @staticmethod
    def code_to_stub(options: LitgenOptions, code: str) -> str:
        generator = LitgenGenerator(options)
        generator._process_cpp_code(code, "")
        r = generator._stub_code()
        return r


def _read_code(options: LitgenOptions, filename: str) -> str:
    assert os.path.isfile(filename)
    with open(filename, "r", encoding=options.srcml_options.encoding) as f:
        code_str = f.read()
    return code_str
