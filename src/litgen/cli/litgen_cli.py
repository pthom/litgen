#!/usr/bin/env python
from __future__ import annotations

import fire  # type: ignore

import litgen
from litgen import cpp_port_helper


class LitgenCliCommands:
    """Command line for srcmlcpp.

    This is a command line driven tool for litgen.
    Once srcmlcpp is installed, the commands below are available via the `litgen` command.

    For example:
        ```bash
        >> litgen stub "int f(int a=1, const float v[2]);"
        def f(a: int = 1, v: List[float]) -> int:
            pass
       ```
    All commands will use default LitgenOptions().
    """

    @staticmethod
    def stub(code: str) -> None:
        """Show generated pyi stub code for the given C++ code, with litgen's default options"""
        options = litgen.LitgenOptions()
        generated_code = litgen.generate_code(options, code)
        print(generated_code.stub_code)

    @staticmethod
    def pydef(code: str) -> None:
        """Show generated C++ pybind11 binding code the given C++ code, with litgen's default options"""
        options = litgen.LitgenOptions()
        generated_code = litgen.generate_code(options, code)
        print(generated_code.pydef_code)

    @staticmethod
    def glue(code: str) -> None:
        """Show generated glue code for the given C++ code, with litgen's default options"""
        options = litgen.LitgenOptions()
        generated_code = litgen.generate_code(options, code)
        print(generated_code.glue_code)

    @staticmethod
    def cpp_to_snake_case(cpp_code: str) -> None:
        """Transforms the functions and decl names into snake case in the given code"""
        r = cpp_port_helper.cpp_to_snake_case(cpp_code)
        print(r)

    @staticmethod
    def cpp_to_python_helper(cpp_code: str) -> None:
        """Transforms the functions and decl names into snake case in the given code,
        then replace "::" by ".", "{" and "}" by ""
        """
        r = cpp_port_helper.cpp_to_python_helper(cpp_code)
        print(r)


def main() -> None:
    fire.Fire(LitgenCliCommands)


if __name__ == "__main__":
    main()
