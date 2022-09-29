from __future__ import annotations
from typing import Set
from dataclasses import dataclass

from litgen.options import LitgenOptions
from litgen.internal.context.type_synonyms import *
from litgen.internal.context.namespaces_code_tree import NamespacesCodeTree, PydefOrStub


@dataclass
class LitgenContext:
    """
    This context store the options, as well as some infos on the encountered types and namespace
    for post-process generation.
    """

    options: LitgenOptions
    encountered_cpp_boxed_types: Set[CppTypeName]
    namespaces_stub: NamespacesCodeTree
    namespaces_pydef: NamespacesCodeTree

    def __init__(self, options: LitgenOptions):
        self.options = options
        self.encountered_cpp_boxed_types = set()
        self.namespaces_stub = NamespacesCodeTree(PydefOrStub.Stub)
        self.namespaces_pydef = NamespacesCodeTree(PydefOrStub.Pydef)
