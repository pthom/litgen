from typing import List, Any
from dataclasses import dataclass

from litgen.options import LitgenOptions

from srcmlcpp.cpp_scope import CppScope


@dataclass
class LitgenWriterContext:

    options: LitgenOptions
    _encountered_namespace_scopes: List[CppScope]

    def __init__(self, options: LitgenOptions):
        self.options = options
        self._encountered_namespace_scopes = []

    def register_namespace_scope(self, adapted_namespace: Any) -> None:
        pass

    def has_encountered_namespace(self, adapted_namespace: Any) -> bool:
        pass

    def store_namespace_stub_code(self, adapted_namespace: Any, code: str) -> None:
        pass

    def str_stub_namespaces(self) -> str:
        pass
