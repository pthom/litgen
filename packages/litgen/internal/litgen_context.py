from typing import List, Any
from dataclasses import dataclass

from litgen.options import LitgenOptions
from litgen.internal.boxed_python_types_registry import BoxedPythonTypesRegistry

from srcmlcpp.cpp_scope import CppScope


@dataclass
class LitgenContext:
    """
    This context store the options, as well as some infos on the encountered types and namespace
    for post-process generation.
    """

    options: LitgenOptions
    _encountered_namespace_scopes: List[CppScope]
    boxed_types_registry: BoxedPythonTypesRegistry

    def __init__(self, options: LitgenOptions):
        self.options = options
        self._encountered_namespace_scopes = []
        self.boxed_types_registry = BoxedPythonTypesRegistry()

    def register_namespace_scope(self, adapted_namespace: Any) -> None:
        pass

    def has_encountered_namespace(self, adapted_namespace: Any) -> bool:
        pass

    def store_namespace_stub_code(self, adapted_namespace: Any, code: str) -> None:
        pass

    def str_stub_namespaces(self) -> str:
        pass
