from __future__ import annotations
from enum import Enum


CppNamespaceName = str
CppQualifiedNamespaceName = str
StubCode = str
Code = str  # can be python or cpp code
CppTypeName = str


class PydefOrStub(Enum):
    Stub = 1
    Pydef = 2
