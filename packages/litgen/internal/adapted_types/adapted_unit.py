from typing import cast

from codemanip.parse_progress_bar import global_progress_bars

from srcmlcpp.srcml_types import CppUnit

from litgen.litgen_context import LitgenContext
from litgen.internal.adapted_types.adapted_block import AdaptedBlock
from litgen.internal.adapted_types.adapted_element import (
    AdaptedElement,
    _PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS,
    _PROGRESS_BAR_TITLE_STUB,
    _PROGRESS_BAR_TITLE_PYDEF,
)


class AdaptedUnit(AdaptedBlock):
    def __init__(self, litgen_writer_context: LitgenContext, unit: CppUnit):
        super().__init__(litgen_writer_context, unit)
        self.options.check_options_consistency()
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS)
        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_ADAPTED_ELEMENTS)

    # override
    def cpp_element(self) -> CppUnit:
        return cast(CppUnit, self._cpp_element)

    def str_stub(self) -> str:
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_STUB)
        r = AdaptedElement.str_stub(self)
        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_STUB)
        return r

    def str_pydef(self) -> str:
        global_progress_bars().start_progress_bar(_PROGRESS_BAR_TITLE_PYDEF)
        r = AdaptedElement.str_pydef(self)
        global_progress_bars().stop_progress_bar(_PROGRESS_BAR_TITLE_PYDEF)
        return r

    # override : not needed, use AdaptedBlock version
    # def _str_stub_lines(self) -> List[str]:
    #     raise ValueError("To be completed")

    # override : not needed, use AdaptedBlock version
    # def _str_pydef_lines(self) -> List[str]:
    #     raise ValueError("To be completed")
