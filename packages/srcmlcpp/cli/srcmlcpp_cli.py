#!/usr/bin/env python
import fire
import srcmlcpp


class CliCommands:
    """Command line for srcmlcpp.

    The is a command line driven tool for srcmlcpp.
    Once srcmlcpp is installed, the commands below are available via the "srcmlcpp" script.

    For example:
        ````bash
       >>  srcmlcpp xml "int a" --beautify=False
        <unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++"><decl><type><name>int</name></type> <name>a</name></decl></unit>
        ````
    All commands will use default SrcmlOptions().
    In order to change them, you will have to customize them via code.
    """

    @staticmethod
    def xml(code, beautify: bool = True):
        """Shows the xml tree parsed by srcML (http://srcml.org)

        * if beautify=False (--beautify=False), the output will be the same as srcML
             echo "int i = 1;" | srcml --language C++
        * otherwise, the xml tree will be beautified and indented
        """
        srcml_options = srcmlcpp.SrcmlOptions()
        srcml_options.flag_srcml_dump_positions = False
        xml_wrapper = srcmlcpp.code_to_srcml_xml_wrapper(srcml_options, code)
        print(xml_wrapper.str_xml(beautify=beautify))

    @staticmethod
    def cpp_overview(code):
        """Shows an overview the AST built by srcmlcpp"""
        srcml_options = srcmlcpp.SrcmlOptions()
        cpp_unit = srcmlcpp.code_to_cpp_unit(srcml_options, code)
        print(cpp_unit.hierarchy_overview())


def main():
    fire.Fire(CliCommands)


if __name__ == "__main__":
    main()
