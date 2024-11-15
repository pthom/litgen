from __future__ import annotations
from typing import TYPE_CHECKING
from codemanip import code_utils

from litgen.internal.context.type_synonyms import Code, CppNamespaceName, CppQualifiedNamespaceName, PydefOrStub


if TYPE_CHECKING:
    from litgen.options import LitgenOptions


class NamespacesCodeTree:
    """Stores namespaces and sub-namespace (modules and submodules in python) code

    Two instances NamespacesCodeTree are stored inside LitgenContext (for pydef and for stub code)

    - they are filled during calls to `AdaptedNamespace._str_stub_lines()` and `AdaptedNamespace._str_pydef_lines()`
      (i.e. AdaptedNamespace does not output code immediately, but stores it in the context)
    - their content is outputted by AdaptedUnit (which calls full_tree_code())
    """

    _namespace_code: Code
    _sub_namespaces_code: dict[CppNamespaceName, NamespacesCodeTree]

    _created_namespaces: set[CppQualifiedNamespaceName]

    _namespace_code_intro: str
    _namespace_code_outro: str
    _code_type: PydefOrStub
    _options: LitgenOptions

    def __init__(self, options: LitgenOptions, code_type: PydefOrStub) -> None:
        self._namespace_code = ""
        self._sub_namespaces_code = {}
        self._created_namespaces = set()
        self._code_type = code_type
        self._options = options

        if code_type == PydefOrStub.Stub:
            self._namespace_code_intro = "\n# <submodule NS_NAME>\n"
            self._namespace_code_outro = "\n# </submodule NS_NAME>\n"
        elif code_type == PydefOrStub.Pydef:
            self._namespace_code_intro = "\n{ // <namespace NS_NAME>\n"
            self._namespace_code_outro = "\n} // </namespace NS_NAME>\n"

    def full_tree_code(self, indent_str: str, current_namespace_name: str = "") -> str:
        from litgen.internal import cpp_to_python

        r = ""

        if len(current_namespace_name) == 0 or len(self._namespace_code) == 0:
            is_namespace_ignored = True
        else:
            is_namespace_ignored = current_namespace_name in self._options.namespaces_root

        ns_written_name = current_namespace_name
        if self._code_type == PydefOrStub.Stub:
            ns_written_name = cpp_to_python.namespace_name_to_python(self._options, ns_written_name)

        if not is_namespace_ignored:
            r += self._namespace_code_intro.replace("NS_NAME", ns_written_name)

        r += self._namespace_code

        for ns_name, sub_namespace_stub_code in self._sub_namespaces_code.items():
            sub_code = sub_namespace_stub_code.full_tree_code(indent_str, ns_name)
            if not is_namespace_ignored:
                sub_code = code_utils.indent_code(sub_code, indent_str=indent_str)
            r += sub_code

        if not is_namespace_ignored:
            r += self._namespace_code_outro.replace("NS_NAME", ns_written_name)

        return r

    def _store_code_in_tree(self, namespace_names: list[CppNamespaceName], code: str) -> None:
        ns_name = namespace_names[0]
        if ns_name not in self._sub_namespaces_code.keys():
            self._sub_namespaces_code[ns_name] = NamespacesCodeTree(self._options, self._code_type)

        sub_code_tree = self._sub_namespaces_code[ns_name]
        if len(namespace_names) == 1:
            # Add new-line between parts if missing
            if len(sub_code_tree._namespace_code) > 0 and (not sub_code_tree._namespace_code.endswith("\n")):
                sub_code_tree._namespace_code += "\n"
            sub_code_tree._namespace_code += code
        else:
            sub_code_tree._store_code_in_tree(namespace_names[1:], code)

    def store_code(self, qualified_namespace_name: CppQualifiedNamespaceName, code: str) -> None:
        namespaces_names = qualified_namespace_name.split("::")

        def shall_use_this_namespace(namespace_name: str) -> bool:
            is_root_namespace = namespace_name in self._options.namespaces_root
            return not is_root_namespace

        namespaces_names = list(filter(shall_use_this_namespace, namespaces_names))

        self._store_code_in_tree(namespaces_names, code)

    def was_namespace_created(self, qualified_namespace_name: CppQualifiedNamespaceName) -> bool:
        r = qualified_namespace_name in self._created_namespaces
        return r

    def register_namespace_creation(self, qualified_namespace_name: CppQualifiedNamespaceName) -> None:
        self._created_namespaces.add(qualified_namespace_name)

    def qualified_namespaces(self) -> set[CppQualifiedNamespaceName]:
        return self._created_namespaces

    def unqualified_namespaces(self) -> set[CppNamespaceName]:
        r = set()
        for ns in self._created_namespaces:
            r.add(ns.split("::")[-1])
        return r
