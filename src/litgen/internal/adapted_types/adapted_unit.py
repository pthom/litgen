from __future__ import annotations
from typing import cast

from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp.cpp_types import CppUnit

from litgen.internal.adapted_types.adapted_block import AdaptedBlock
from litgen.internal.adapted_types.adapted_element import (
    _PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS,
    _PROGRESS_BAR_TITLE_PYDEF,
    _PROGRESS_BAR_TITLE_STUB,
    AdaptedElement,
)
from litgen.internal.context.litgen_context import LitgenContext


class AdaptedUnit(AdaptedBlock):
    def __init__(self, lg_context: LitgenContext, unit: CppUnit):
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS)
        super().__init__(lg_context, unit)
        self.options.check_options_consistency()
        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS)

    # override
    def cpp_element(self) -> CppUnit:
        return cast(CppUnit, self._cpp_element)

    def str_stub(self) -> str:
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_STUB)
        r = AdaptedElement.str_stub(self)

        context_namespaces_code = self.lg_context.namespaces_stub.full_tree_code(self.options._indent_python_spaces())
        r += context_namespaces_code

        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_STUB)
        return r

    def str_pydef(self) -> str:
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_PYDEF)
        r = AdaptedElement.str_pydef(self)

        context_namespaces_code = self.lg_context.namespaces_pydef.full_tree_code(self.options._indent_cpp_spaces())
        r += context_namespaces_code

        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_PYDEF)
        return r

    # override : not needed, use AdaptedBlock version
    # def _str_stub_lines(self) -> List[str]:
    #     raise ValueError("To be completed")

    # override : not needed, use AdaptedBlock version
    # def _str_pydef_lines(self) -> List[str]:
    #     raise ValueError("To be completed")
