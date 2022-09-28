from __future__ import annotations
from typing import Dict, List

from codemanip import code_utils

from litgen.internal.context.type_synonyms import *


class NamespacesStubCodeTree:
    _namespaces_stub_code: Dict[CppNamespaceName, StubCode]
    _sub_namespaces_stub_code: Dict[CppNamespaceName, NamespacesStubCodeTree]

    def __init__(self) -> None:
        self._namespaces_stub_code = {}
        self._sub_namespaces_stub_code = {}

    def _store_namespace_stub_code_in_tree(self, namespace_names: List[CppNamespaceName], code: str):
        ns_name = namespace_names[0]
        if len(namespace_names) == 1:
            if ns_name not in self._namespaces_stub_code.keys():
                self._namespaces_stub_code[ns_name] = ""
            self._namespaces_stub_code[ns_name] += code
        else:
            if ns_name not in self._sub_namespaces_stub_code.keys():
                self._sub_namespaces_stub_code[ns_name] = NamespacesStubCodeTree()
            self._sub_namespaces_stub_code[ns_name]._store_namespace_stub_code_in_tree(namespace_names[1:], code)

    def store_namespace_stub_code(self, qualified_namespace_name: CppQualifiedNamespaceName, code: str) -> None:
        namespaces_names = qualified_namespace_name.split("::")
        self._store_namespace_stub_code_in_tree(namespaces_names, code)

    def stub_code(self, indent_str: str) -> str:
        r = ""
        for namespace_stub_code in self._namespaces_stub_code.values():
            r += namespace_stub_code
        for sub_namespace_stub_code in self._sub_namespaces_stub_code.values():
            sub_code = sub_namespace_stub_code.stub_code(indent_str)
            r += code_utils.indent_code(sub_code, indent_str=indent_str)
        return r
