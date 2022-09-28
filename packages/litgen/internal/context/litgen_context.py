from __future__ import annotations
from typing import Set
from dataclasses import dataclass

from litgen.options import LitgenOptions
from litgen.internal.context.type_synonyms import *
from litgen.internal.context.namespaces_code_tree import NamespacesStubCodeTree


@dataclass
class LitgenContext:
    """
    This context store the options, as well as some infos on the encountered types and namespace
    for post-process generation.
    """

    options: LitgenOptions
    encountered_cpp_boxed_types: Set[CppTypeName]
    created_cpp_namespaces: Set[CppQualifiedNamespaceName]
    namespaces_stub_code_tree: NamespacesStubCodeTree

    def __init__(self, options: LitgenOptions):
        self.options = options
        self.encountered_cpp_boxed_types = set()
        self.created_cpp_namespaces = set()
        self.namespaces_stub_code_tree = NamespacesStubCodeTree()
