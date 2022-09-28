from dataclasses import dataclass
from typing import List, cast
from munch import Munch  # type: ignore

from codemanip import code_utils

from srcmlcpp.srcml_types import CppNamespace

from litgen.internal.context.litgen_context import LitgenContext
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_block import AdaptedBlock
from litgen.internal import cpp_to_python


@dataclass
class AdaptedNamespace(AdaptedElement):
    adapted_block: AdaptedBlock

    def __init__(self, lg_context: LitgenContext, namespace_: CppNamespace) -> None:
        super().__init__(lg_context, namespace_)
        self.adapted_block = AdaptedBlock(self.lg_context, self.cpp_element().block)

    def namespace_name(self) -> str:
        return self.cpp_element().ns_name

    def flag_create_python_namespace(self) -> bool:
        is_root = code_utils.does_match_regex(self.options.namespace_root__regex, self.namespace_name())
        return not is_root

    # override
    def cpp_element(self) -> CppNamespace:
        return cast(CppNamespace, self._cpp_element)

    # override
    def _str_stub_lines(self) -> List[str]:
        # raise ValueError("To be completed")
        lines: List[str] = []

        _i_ = self.options.indent_python_spaces()
        ns_name = self.namespace_name()

        proxy_class_code = code_utils.unindent_code(
            f"""
            class {ns_name}: # Proxy class that introduces the C++ namespace {ns_name}
            {_i_}# This class actually represents a namespace: all its method are static!
            """,
            flag_strip_empty_lines=True,
        )

        docstring_lines = cpp_to_python.docstring_lines(self.options, self.cpp_element())
        lines.append(f"# <namespace {self.namespace_name()}>")
        self.cpp_element().cpp_element_comments.full_comment()
        if self.flag_create_python_namespace():
            lines += proxy_class_code.split("\n")
            lines += code_utils.indent_code_lines(
                docstring_lines + self.adapted_block._str_stub_lines(), indent_str=_i_
            )
        else:
            lines += docstring_lines
            lines += self.adapted_block._str_stub_lines()
        lines.append(f"# </namespace {self.namespace_name()}>")
        lines.append("")

        if self.flag_create_python_namespace():
            namespace_qualified_name = self.cpp_element().cpp_scope(include_self=True).str_cpp()
            code = "\n".join(lines)
            self.lg_context.namespaces_stub_code_tree.store_namespace_stub_code(namespace_qualified_name, code)
            return []
        else:
            return lines

    def _pydef_make_submodule_code(self) -> str:
        namespace_qualified_name = self.cpp_element().cpp_scope(include_self=True).str_cpp()
        if namespace_qualified_name in self.lg_context.created_cpp_namespaces:
            return ""

        self.lg_context.created_cpp_namespaces.add(namespace_qualified_name)

        submodule_code_template = (
            'py::module_ {submodule_cpp_var} = {parent_module_cpp_var}.def_submodule("{module_name}", "{module_doc}");'
        )

        replace_tokens = Munch()

        replace_tokens.parent_module_cpp_var = cpp_to_python.cpp_scope_to_pybind_parent_var_name(
            self.options, self.cpp_element()
        )
        replace_tokens.submodule_cpp_var = cpp_to_python.cpp_scope_to_pybind_var_name(self.options, self.cpp_element())

        replace_tokens.module_doc = cpp_to_python.comment_pydef_one_line(
            self.options, self.cpp_element().cpp_element_comments.full_comment()
        )

        replace_tokens.module_name = self.namespace_name()

        submodule_code_ = code_utils.process_code_template(
            input_string=submodule_code_template,
            replacements=replace_tokens,
            replacements_with_line_removal_if_not_found={},
        )
        return submodule_code_

    # override
    def _str_pydef_lines(self) -> List[str]:
        location = self.info_original_location_cpp()
        namespace_name = self.namespace_name()
        block_code_lines = self.adapted_block._str_pydef_lines()

        lines: List[str] = []

        lines.append(f"// <namespace {namespace_name}>{location}")
        if self.flag_create_python_namespace():
            submodule_code = self._pydef_make_submodule_code()
            lines += [submodule_code]
            lines += block_code_lines
        else:
            lines += block_code_lines
        lines.append(f"// </namespace {namespace_name}>")
        return lines
