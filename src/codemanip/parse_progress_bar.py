from __future__ import annotations


class _ParseStepProgressBar:
    """Console progress bar showing the progress of a parsing step in a given file"""

    _nb_total_lines: int = 0
    _current_line: int = 0
    _step_name: str = ""

    def __init__(self, nb_total_lines: int, step_name: str) -> None:
        self._nb_total_lines = nb_total_lines
        self._step_name = step_name
        self._current_line = 0

    def start(self, description: str) -> None:
        self._current_line = 0
        self._step_name = description

    def stop(self) -> None:
        print()
        pass

    def set_current_line(self, current_line: int) -> None:
        if current_line < 0:
            return
        progress = current_line - self._current_line
        if progress < 0:
            return
        self._current_line = current_line
        self._display()

    def _display(self) -> None:
        advance_info = ""
        if self._nb_total_lines > 0:
            ratio = self._current_line / self._nb_total_lines * 100
            advance_info = f"{ratio:.1f}% - Line {self._current_line}/{self._nb_total_lines}"
        else:
            advance_info = f"Line {self._current_line}"
        spacing = "                        "
        print(f"{self._step_name} {advance_info}{spacing}", end="\r")


class ParseProgressBars:
    """Handle several progress bars for different parsing states"""

    _progress_bars: dict[str, _ParseStepProgressBar]
    _nb_total_lines: int = 0
    _enabled: bool = True

    def __init__(self) -> None:
        self._progress_bars = {}

    def set_nb_total_lines(self, nb_total_lines: int) -> None:
        self._nb_total_lines = nb_total_lines

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def start_progress_bar(self, step_name: str) -> None:
        if not self._enabled:
            return
        # assert step_name not in self._progress_bars
        self._progress_bars[step_name] = _ParseStepProgressBar(self._nb_total_lines, step_name)

    def stop_progress_bar(self, step_name: str) -> None:
        if not self._enabled:
            return
        # assert step_name in self._progress_bars
        self._progress_bars[step_name].stop()
        self._progress_bars.pop(step_name)

    def set_current_line(self, step_name: str, current_line: int) -> None:
        if not self._enabled:
            return
        if step_name not in self._progress_bars:
            return
        assert step_name in self._progress_bars
        if step_name in self._progress_bars:
            # -1 because srcml numbering starts at 1
            self._progress_bars[step_name].set_current_line(current_line - 1)


_PARSE_PROGRESS_BARS = ParseProgressBars()


def global_progress_bars() -> ParseProgressBars:
    return _PARSE_PROGRESS_BARS


def tqdm_demo():
    pass


#     from tqdm import tqdm
#     from time import sleep
#     progress1 = tqdm(total=10, desc="Progress 1")
#     progress2 = tqdm(total=100, desc="Inner")
#     for i in range(10):
#         sleep(0.001)
#         progress1.update(1)
#         progress2.reset()
#         for j in range(100):
#             sleep(0.001)
#             progress2.update(1)
#     progress1.__del__()
#     del progress2
