from __future__ import annotations
from typing import Optional
from dataclasses import dataclass


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
