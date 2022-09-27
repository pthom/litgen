from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

from codemanip import code_utils

from litgen.options import LitgenOptions

CppHeaderCode = str
CppPydefCode = str
PythonStubCode = str
Filename = str


@dataclass
class CppFile:
    filename: Optional[str]
    code: str

    def __init__(self, options: LitgenOptions, filename: Optional[str] = None, code: Optional[str] = None):
        if filename is None and code is None:
            raise ValueError("filename and code cannot be None together")
        self.filename = filename

        if code is None:
            assert filename is not None  # make mypy happy
            with open(filename, "r", encoding=options.srcml_options.encoding) as f:
                self.code = f.read()
        else:
            self.code = code


class GeneratedCodeForOneFile:
    filename: str
    pydef_code: CppPydefCode = ""
    stub_code: PythonStubCode = ""

    def __init__(self, filename: str):
        self.filename = filename


class GeneratedBoxedTypeCode:
    generated_code: GeneratedCodeForOneFile
    boxed_types_cpp_declaration: CppHeaderCode

    def __init__(self, filename: str) -> None:
        self.generated_code = GeneratedCodeForOneFile(filename)
        self.boxed_types_cpp_declaration = ""


@dataclass
class GeneratedCode:
    pydef_code: CppPydefCode
    stub_code: PythonStubCode
    boxed_types_cpp_declaration: Optional[CppHeaderCode]

    def __init__(
        self,
        generated_one_files: List[GeneratedCodeForOneFile],
        generated_boxed_type_code: Optional[GeneratedBoxedTypeCode],
        add_boxed_types_definitions: bool,
        options: LitgenOptions,
    ):
        def decorate_filename(filename: str, is_end: bool, decoration_token: str) -> str:
            end_marker = "/" if is_end else ""
            decoration = decoration_token * 20
            r = f"{decoration}    <{end_marker}generated_from:{filename}>    {decoration}\n"
            return r

        def decorate_code(filename: Optional[str], code: str, decoration_token: str) -> str:
            r = ""
            if filename is not None and len(filename) > 0:
                filename_short = code_utils.filename_with_n_parent_folders(
                    filename, options.original_location_nb_parent_folders
                )
                intro = decorate_filename(filename_short, False, decoration_token)
                outro = decorate_filename(filename_short, True, decoration_token)
            else:
                intro = ""
                outro = ""

            r += intro + code + outro
            return r

        self.stub_code = ""
        self.pydef_code = ""

        if add_boxed_types_definitions and generated_boxed_type_code is not None:
            self.pydef_code += decorate_code("BoxedTypes", generated_boxed_type_code.generated_code.pydef_code, "/")
            self.stub_code += decorate_code("BoxedTypes", generated_boxed_type_code.generated_code.stub_code, "#")

        for generated_one_file in generated_one_files:
            filename = generated_one_file.filename
            self.pydef_code += decorate_code(filename, generated_one_file.pydef_code, "/")
            self.stub_code += decorate_code(filename, generated_one_file.stub_code, "#")

        if add_boxed_types_definitions and generated_boxed_type_code is not None:
            self.boxed_types_cpp_declaration = generated_boxed_type_code.boxed_types_cpp_declaration
        else:
            self.boxed_types_cpp_declaration = None
