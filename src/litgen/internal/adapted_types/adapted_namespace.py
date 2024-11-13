from __future__ import annotations
from dataclasses import dataclass
from typing import cast

from munch import Munch  # type: ignore

from codemanip import code_utils
from litgen import BindLibraryType

from srcmlcpp.cpp_types import CppNamespace

from litgen.internal import cpp_to_python
from litgen.internal.adapted_types.adapted_block import AdaptedBlock
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.context.litgen_context import LitgenContext


@dataclass
class AdaptedNamespace(AdaptedElement):
    adapted_block: AdaptedBlock

    def __init__(self, lg_context: LitgenContext, namespace_: CppNamespace) -> None:
        super().__init__(lg_context, namespace_)
        self.adapted_block = AdaptedBlock(self.lg_context, self.cpp_element().block)

    def namespace_name(self) -> str:
        return self.cpp_element().ns_name

    def flag_shall_create_namespace_as_module(self) -> bool:
        is_root = self.namespace_name() in self.options.namespaces_root
        return not is_root

    # override
    def cpp_element(self) -> CppNamespace:
        return cast(CppNamespace, self._cpp_element)

    def _qualified_namespace_name(self) -> str:
        ns_qualified_name = self.cpp_element().cpp_scope_str(include_self=True)
        return ns_qualified_name

    def _stub_class_as_ns_creation_code(self) -> list[str]:
        if self.lg_context.namespaces_stub.was_namespace_created(self._qualified_namespace_name()):
            return []
        self.lg_context.namespaces_stub.register_namespace_creation(self._qualified_namespace_name())

        ns_name = cpp_to_python.namespace_name_to_python(self.options, self.namespace_name())
        _i_ = self.options._indent_python_spaces()
        proxy_class_code = code_utils.unindent_code(
            f"""
            class {ns_name}:  # Proxy class that introduces typings for the *submodule* {ns_name}
            {_i_}pass  # (This corresponds to a C++ namespace. All method are static!)
            """,
            flag_strip_empty_lines=True,
        )
        r = proxy_class_code.split("\n")
        return r

    # override
    def stub_lines(self) -> list[str]:
        lines: list[str] = []
        if (
            not self.lg_context.namespaces_stub.was_namespace_created(self._qualified_namespace_name())
            and self.flag_shall_create_namespace_as_module()
        ):
            lines += cpp_to_python.docstring_lines(self.options, self.cpp_element())
        lines += self.adapted_block.stub_lines()
        lines.append("")

        if self.flag_shall_create_namespace_as_module():
            context_stored_lines = self._stub_class_as_ns_creation_code()
            context_stored_lines += code_utils.indent_code_lines(lines, indent_str=self.options._indent_python_spaces())
            self.lg_context.namespaces_stub.store_code(
                self._qualified_namespace_name(), "\n".join(context_stored_lines)
            )
            return []
        else:
            return lines

    def _pydef_def_submodule_code(self) -> list[str]:
        if self.lg_context.namespaces_pydef.was_namespace_created(self._qualified_namespace_name()):
            return []
        self.lg_context.namespaces_pydef.register_namespace_creation(self._qualified_namespace_name())

        submodule_code_template = '{py}::module_ {submodule_cpp_var} = {parent_module_cpp_var}.def_submodule("{module_name}", "{module_doc}");'

        replace_tokens = Munch()
        replace_tokens.py = "py" if self.options.bind_library == BindLibraryType.pybind11 else "nb"
        replace_tokens.parent_module_cpp_var = cpp_to_python.cpp_scope_to_pybind_parent_var_name(
            self.options, self.cpp_element()
        )
        replace_tokens.submodule_cpp_var = cpp_to_python.cpp_scope_to_pybind_var_name(self.options, self.cpp_element())

        replace_tokens.module_doc = cpp_to_python.comment_pydef_one_line(
            self.options, self.cpp_element().cpp_element_comments.full_comment()
        )

        replace_tokens.module_name = cpp_to_python.namespace_name_to_python(self.options, self.namespace_name())

        submodule_code_ = code_utils.process_code_template(
            input_string=submodule_code_template,
            replacements=replace_tokens,
            replacements_with_line_removal_if_not_found={},
        )
        return submodule_code_.split("\n")

    # override
    def pydef_lines(self) -> list[str]:
        lines = self.adapted_block.pydef_lines()

        if self.flag_shall_create_namespace_as_module():
            context_stored_lines = self._pydef_def_submodule_code() + lines
            context_stored_lines = code_utils.indent_code_lines(
                context_stored_lines, indent_str=self.options._indent_cpp_spaces()
            )
            self.lg_context.namespaces_pydef.store_code(
                self._qualified_namespace_name(), "\n".join(context_stored_lines)
            )
            return []
        else:
            return lines
