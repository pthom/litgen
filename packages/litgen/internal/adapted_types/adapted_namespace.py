from dataclasses import dataclass
from typing import List, cast

from codemanip import code_utils

from srcmlcpp.srcml_types import CppNamespace

from litgen import LitgenOptions
from litgen.internal.adapted_types.adapted_element import AdaptedElement
from litgen.internal.adapted_types.adapted_block import AdaptedBlock


@dataclass
class AdaptedNamespace(AdaptedElement):
    adapted_block: AdaptedBlock

    def __init__(self, options: LitgenOptions, namespace_: CppNamespace) -> None:
        super().__init__(options, namespace_)
        self.adapted_block = AdaptedBlock(self.options, self.cpp_element().block)

    def namespace_name(self) -> str:
        return self.cpp_element().ns_name

    def flag_create_python_namespace(self):
        return False

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
            f'''
            class {ns_name}:
            {_i_}"""Proxy class that introduces the C++ namespace {ns_name}
            {_i_}This class actually represents a namespace: all its method are static!"""
            {_i_}def __init__(self):
            {_i_}{_i_}raise RuntimeError("This class corresponds to a namespace!")
        ''',
            flag_strip_empty_lines=True,
        )

        lines.append(f"# <namespace {self.namespace_name()}>")
        if self.flag_create_python_namespace():
            lines += proxy_class_code.split("\n")
            lines += code_utils.indent_code_lines(self.adapted_block._str_stub_lines(), indent_str=_i_)
        else:
            lines += self.adapted_block._str_stub_lines()
        lines.append(f"# </namespace {self.namespace_name()}>")
        lines.append("")

        return lines

    # override
    def _str_pydef_lines(self) -> List[str]:
        location = self.info_original_location_cpp()
        namespace_name = self.namespace_name()
        block_code_lines = self.adapted_block._str_pydef_lines()

        lines: List[str] = []
        lines.append(f"// <namespace {namespace_name}>{location}")
        lines += block_code_lines
        lines.append(f"// </namespace {namespace_name}>")
        return lines
