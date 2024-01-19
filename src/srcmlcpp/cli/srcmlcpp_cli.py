#!/usr/bin/env python
from __future__ import annotations

import fire  # type: ignore

import srcmlcpp


class SrcmlcppCliCommands:
    """Command line for srcmlcpp.

    This is a command line driven tool for srcmlcpp.
    Once srcmlcpp is installed, the commands below are available via the `srcmlcpp` command.

    For example:
        ```bash
        >> srcmlcpp cpp_elements "int a = 1;"
        CppUnit
          CppDeclStatement
            CppDecl name=a
              CppType name=int

        >>  srcmlcpp xml "int a = 1;" --beautify=False
        <unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++"><decl_stmt><decl><type><name>int</name></type> <name>a</name><init>=<expr><literal type="number">1</literal></expr></init></decl>;</decl_stmt></unit>
       ```
    All commands will use default SrcmlcppOptions().
    """

    @staticmethod
    def cpp_elements(code: str) -> None:
        """Shows an overview the CppElements tree built by srcmlcpp"""
        srcmlcpp_options = srcmlcpp.SrcmlcppOptions()
        cpp_unit = srcmlcpp.code_to_cpp_unit(srcmlcpp_options, code)
        print(cpp_unit.hierarchy_overview())

    @staticmethod
    def xml(code: str, beautify: bool = True, position: bool = False) -> None:
        """Shows the xml tree parsed by srcML (http://srcml.org)

        * if beautify=False (--beautify=False), the output will be similar to the bare srcML output.
          otherwise, the xml tree will be beautified and indented
        * if position = True, then the code elements positions will be dumped in the xml tree
        """
        srcmlcpp_options = srcmlcpp.SrcmlcppOptions()
        srcmlcpp_options.flag_srcml_dump_positions = position
        xml_wrapper = srcmlcpp.code_to_srcml_wrapper(srcmlcpp_options, code)
        print(xml_wrapper.str_xml(beautify=beautify))


def main() -> None:
    fire.Fire(SrcmlcppCliCommands)


if __name__ == "__main__":
    main()
