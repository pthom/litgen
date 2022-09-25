from typing import List


class BoxedPythonTypesRegistry:
    cpp_boxed_types: List[str]

    def __init__(self) -> None:
        self.cpp_boxed_types = []

    def register_cpp_type(self, cpp_type: str) -> None:
        if cpp_type not in self.cpp_boxed_types:
            self.cpp_boxed_types.append(cpp_type)

    def clear(self) -> None:
        self.cpp_boxed_types = []
