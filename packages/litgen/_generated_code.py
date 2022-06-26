from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

from litgen.options import LitgenOptions

CppHeaderCode = str
CppPydefCode = str
PythonStubCode = str
Filename = str


@dataclass
class GeneratedCode:
    cpp_header_code: CppHeaderCode = ""
    pydef_code: CppPydefCode = ""
    stub_code: PythonStubCode = ""
    boxed_types_generated_code: Optional[GeneratedCode] = None


@dataclass
class CppHeaderCodeWithOptions:
    options: LitgenOptions
    filename: Optional[str]
    code: Optional[str]

    def __init__(self, options: LitgenOptions, filename: Optional[str] = None, code: Optional[str] = None):
        if filename is None and code is None:
            raise ValueError("filename and code cannot be None together")
        self.options = options
        self.filename = filename
        self.code = code


@dataclass
class CppHeadersCodeWithOptionsList:
    headers_and_options_list: List[CppHeaderCodeWithOptions]

    def __init__(self, headers_and_options_list: List[CppHeaderCodeWithOptions]) -> None:
        self.headers_and_options_list = headers_and_options_list

    @staticmethod
    def from_options_and_one_header(options: LitgenOptions, filename: Optional[str] = None, code: Optional[str] = None):
        """named constructor for cases where there is only one file or code string"""
        a = CppHeaderCodeWithOptions(options, filename, code)
        headers_and_options_list = [CppHeaderCodeWithOptions(options, filename, code)]
        r = CppHeadersCodeWithOptionsList(headers_and_options_list)
        return r
