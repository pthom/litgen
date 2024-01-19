from __future__ import annotations
from codemanip import code_utils

from dataclasses import dataclass


@dataclass
class _ClassIterableInfo:
    python_class_name__regex: str
    python_iterable_type: str


class ClassIterablesInfos:
    class_iterable_infos: list[_ClassIterableInfo]

    def __init__(self) -> None:
        self.class_iterable_infos = []

    def is_class_iterable(self, python_class_name: str) -> bool:
        for class_iterable_info in self.class_iterable_infos:
            if code_utils.does_match_regex(class_iterable_info.python_class_name__regex, python_class_name):
                return True
        return False

    def python_iterable_type(self, python_class_name: str) -> str:
        assert self.is_class_iterable(python_class_name)
        for class_iterable_info in self.class_iterable_infos:
            if code_utils.does_match_regex(class_iterable_info.python_class_name__regex, python_class_name):
                return class_iterable_info.python_iterable_type
        return ""

    def add_iterable_class(self, python_class_name__regex: str, python_iterable_type: str) -> None:
        self.class_iterable_infos.append(_ClassIterableInfo(python_class_name__regex, python_iterable_type))
