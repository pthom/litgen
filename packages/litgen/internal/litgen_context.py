from typing import Dict, Set
from dataclasses import dataclass

from litgen.options import LitgenOptions
from srcmlcpp.cpp_scope import CppScope


CppQualifiedNamespaceName = str
StubCode = str
CppTypeName = str


class NamespacesStubCode:
    _namespaces_stub_code: Dict[CppQualifiedNamespaceName, StubCode]

    def __init__(self) -> None:
        self._namespaces_stub_code = {}

    def store_namespace_stub_code(self, namespace_scope: CppScope, code: str) -> None:
        ns_name = namespace_scope.str_cpp()
        if ns_name not in self._namespaces_stub_code.keys():
            self._namespaces_stub_code[ns_name] = ""
        self._namespaces_stub_code[ns_name] += code


@dataclass
class LitgenContext:
    """
    This context store the options, as well as some infos on the encountered types and namespace
    for post-process generation.
    """

    options: LitgenOptions
    encountered_cpp_boxed_types: Set[CppTypeName]
    created_cpp_namespaces: Set[CppQualifiedNamespaceName]
    namespaces_stub_code: NamespacesStubCode

    def __init__(self, options: LitgenOptions):
        self.options = options
        self.encountered_cpp_boxed_types = set()
        self.created_cpp_namespaces = set()
        self.namespaces_stub_code = NamespacesStubCode()
