#!/usr/bin/env python
import fire  # type: ignore

import litgen


class LitgenCliCommands:
    """Command line for srcmlcpp.

    This is a command line driven tool for litgen.
    Once srcmlcpp is installed, the commands below are available via the `litgen` command.

    For example:
        ````bash
        >> litgen stub "int f(int a=1, const float v[2]);"
        def f(a: int = 1, v: List[float]) -> int:
            pass
       ````
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


def main() -> None:
    fire.Fire(LitgenCliCommands)


if __name__ == "__main__":
    main()
