"""
Interface to srcML (https://www.srcml.org/)
"""

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
import time

from srcml_types import *


class SrcMlException(Exception):
    pass


###########################################
#
# code_to_srcml / srcml_to_code, etc (call program srcml)
#
###########################################


def _embed_element_into_unit(element: ET.Element) -> ET.Element:
    if element.tag.endswith("unit"):
        return element
    else:
        new_element = ET.Element("unit")
        new_element.append(element)
        return new_element


class _TimeStats:
    nb_calls: int  = 0
    total_time: float = 0.
    _last_start_time: float = 0.
    def start(self):
        self.nb_calls += 1
        self._last_start_time = time.time()
    def stop(self):
        self.total_time += time.time() - self._last_start_time
    def stats_string(self) -> str:
        return f"calls: {self.nb_calls} total time: {self.total_time:.3f}s average: {self.total_time / self.nb_calls * 1000:.0f}ms"



class _SrcmlCaller:
    _stats_code_to_srcml: _TimeStats = _TimeStats()
    _stats_srcml_to_code: _TimeStats = _TimeStats()

    def _call_subprocess(self, input_filename, output_filename, dump_positions: bool):
        position_arg = "--position" if dump_positions else ""

        shell_command = f"srcml -l C++ {input_filename} {position_arg} --xml-encoding utf-8 --src-encoding utf-8 -o {output_filename}"
        logging.debug(f"_SrcmlCaller.call: {shell_command}")
        try:
            subprocess.check_call(shell_command, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"_SrcmlCaller.call, error {e}")
            raise

    def code_to_srcml(self, input_str, dump_positions: bool = False) -> ET.Element:
        """
        Calls srcml with the given code and return the srcml as xml Element
        """
        self._stats_code_to_srcml.start()
        with tempfile.NamedTemporaryFile(suffix=".h", delete=False) as input_header_file:
            input_header_file.write(input_str.encode("utf-8"))
            input_header_file.close()
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as output_xml_file:
                self._call_subprocess(input_header_file.name, output_xml_file.name, dump_positions)
                output_bytes = output_xml_file.read()
                os.remove(output_xml_file.name)
            os.remove(input_header_file.name)

        output_str = output_bytes.decode("utf-8")
        element = ET.fromstring(output_str)
        self._stats_code_to_srcml.stop()
        return element

    def srcml_to_code(self, element: ET.Element) -> str:
        """
        Calls srcml with the given srcml xml element and return the corresponding code
        """
        self._stats_srcml_to_code.start()
        unit_element = _embed_element_into_unit(element)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as input_xml_file:
            element_tree = ET.ElementTree(unit_element)
            element_tree.write(input_xml_file.name)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".h") as output_header_file:
                self._call_subprocess(input_xml_file.name, output_header_file.name, False)
                output_bytes = output_header_file.read()
                os.remove(output_header_file.name)
        os.remove(input_xml_file.name)

        code_str = output_bytes.decode("utf-8")
        self._stats_srcml_to_code.stop()
        return code_str


    def __del__(self):
        print(f"_SrcmlCaller: code_to_srcml {self._stats_code_to_srcml.stats_string()}    |    srcml_to_code {self._stats_srcml_to_code.stats_string()}")


_SRCML_CALLER = _SrcmlCaller()


def code_to_srcml(code: str, dump_positions: bool = False) -> ET.Element:
    return _SRCML_CALLER.code_to_srcml(code, dump_positions)


def srcml_to_code(element: ET.Element) -> str:
    return _SRCML_CALLER.srcml_to_code(element)


###########################################
#
# Parsing
#
###########################################


def parse_name(element: ET.Element) -> str:
    """
    https://www.srcml.org/doc/cpp_srcML.html#name

    For names, we always reproduce the original code (i.e we reassemble the sub-elements)
    """
    assert clean_tag(element.tag) == "name"
    if element.text is not None:
        return element.text
    else:
        return srcml_to_code(element)


def parse_type(element: ET.Element, previous_decl: CppDecl) -> CppType:
    """
    https://www.srcml.org/doc/cpp_srcML.html#type
    """
    assert clean_tag(element.tag) == "type"
    result = CppType()
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "name":
            result.name = parse_name(child)
        elif child_tag == "specifier":
            result.specifiers.append(child.text)
        elif child_tag == "modifier":
            result.modifiers.append(child.text)
        else:
            raise SrcMlException(f"Unexpected tag in parse_type: {child_tag}")

    if len(result.name) == 0:
        assert previous_decl is not None
        result.name = previous_decl.cpp_type.name

    return result


def parse_cpp_decl(element: ET.Element, previous_decl: CppDecl) -> CppDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement

    Note: init_cpp is inside an <init><expr> node in srcML. Here we retransform it to C++ code for simplicity
        For example:
            int a = 5;
            <decl_stmt><decl><type><name>int</name></type> <name>a</name> <init>= <expr><literal type="number">5</literal></expr></init></decl>;</decl_stmt>
    """
    assert clean_tag(element.tag) == "decl"
    result = CppDecl()
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "type":
            result.cpp_type = parse_type(child, previous_decl)
        elif child_tag == "name":
            result.name = child.text
        elif child_tag == "init":
            expr_child = child_with_tag(child, "expr")
            result.init = srcml_to_code(expr_child)
        else:
            raise SrcMlException(f"Unexpected tag in parse_cpp_decl: {child_tag}")
    return result


def parse_cpp_decl_stmt(element: ET.Element) -> CppDeclStatement:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """
    assert clean_tag(element.tag) == "decl_stmt"

    previous_decl: CppDecl = None
    result = CppDeclStatement()
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "decl":
            cpp_decl = parse_cpp_decl(child, previous_decl)
            result.cpp_decls.append(cpp_decl)
            previous_decl = cpp_decl
        else:
            raise SrcMlException(f"Unexpected tag in parse_cpp_decl_statement: {child_tag}")
    return result


def parse_parameter(element: ET.Element) -> CppParameter:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag(element.tag) == "parameter"
    result = CppParameter()
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "decl":
            result.decl = parse_cpp_decl(child, None)
        else:
            raise SrcMlException(f"Unexpected tag in parse_parameter: {parse_parameter}")

    if len(result.decl.name) == 0:
        raise SrcMlException(f"Found no name in parse_parameter!")

    return result


def parse_parameter_list(element: ET.Element) -> CppParameterList:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag(element.tag) == "parameter_list"
    result = CppParameterList()
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "parameter":
            result.parameters.append(parse_parameter(child))
        else:
            raise SrcMlException(f"Unexpected tag in parse_parameter_list: {child_tag}")
    return result


def parse_function_decl(element: ET.Element) -> CppFunctionDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    assert clean_tag(element.tag) == "function_decl"
    result = CppFunctionDecl()

    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == "type":
            result.type = parse_type(child, None)
        elif child_tag == "name":
            result.name = parse_name(child)
        elif child_tag == "parameter_list":
            result.parameter_list = parse_parameter_list(child)
        else:
            raise SrcMlException(f"Unexpected tag in parse_function_decl: {child_tag}")

    return result



###########################################
#
# Utilities
#
###########################################


def children_with_tag(element: ET.Element, tag: str) -> List[ET.Element]:
    r = []
    for child in element:
        child_tag = clean_tag(child.tag)
        if child_tag == tag:
            r.append(child)
    return r


def child_with_tag(element: ET.Element, tag: str) -> ET.Element:
    children = children_with_tag(element, tag)
    if len(children) == 0:
        raise SrcMlException(f"child_with_tag: did not find child with tag {tag}")
    elif len(children) > 1:
        raise SrcMlException(f"child_with_tag: found more than one child with tag {tag}")
    return  children[0]


def first_code_element_with_tag(code: str, tag: str) -> ET.Element:
    """
    Utility for tests: extracts the first xml element of type "decl_stmt"
    """
    root = code_to_srcml(code)
    return child_with_tag(root, tag)


def srcml_to_str(element: ET.Element):
    xmlstr = minidom.parseString(ET.tostring(element)).toprettyxml(indent="   ")
    return xmlstr


def srcml_to_file(root: ET.Element, filename: str):
    element_tree = ET.ElementTree(root)
    element_tree.write(filename, encoding="utf-8")


def clean_tag(tag_name: str) -> str:
    return tag_name.replace("{http://www.srcML.org/srcML/src}", "")

