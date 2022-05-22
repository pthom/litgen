"""
Interface to srcML (https://www.srcml.org/)
"""

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.dom import minidom

from srcml_types import *


class SrcMlException(Exception):
    pass


###########################################
#
# code_to_srcml / srcml_to_code, etc (call program srcml)
#
###########################################


class _CountSrcmlCalls:
    nb_calls: int = 0
    def ping(self):
        self.nb_calls += 1
    def __del__(self):
        print(f"CountSrcmlCalls: {self.nb_calls} calls")


_COUNT_SRCML_CALLS = _CountSrcmlCalls()



def code_to_srcml(code: str, dump_positions: bool = False) -> ET.Element:
    """
    Calls srcml with the given code and return the xml as a string
    """

    position_arg = "--position" if dump_positions else ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".h") as cpp_header_file:
        cpp_header_file.write(code.encode("utf-8"))
        cpp_header_file.close()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as xml_file:
            cmd = f"srcml -l C++ {cpp_header_file.name} {position_arg} --xml-encoding utf-8 --src-encoding utf-8 -o {xml_file.name}"
            try:
                # print(cmd)
                _COUNT_SRCML_CALLS.ping()
                subprocess.check_call(cmd, shell=True)
                srcml_bytes = xml_file.read()
            except subprocess.CalledProcessError as e:
                print(f"code_to_srcml, error: {e}")
                raise
            finally:
                os.remove(cpp_header_file.name)
                os.remove(xml_file.name)

    srcml_str = srcml_bytes.decode("utf-8")
    element = ET.fromstring(srcml_str)
    return element


def _embed_element_into_unit(element: ET.Element) -> ET.Element:
    if element.tag.endswith("unit"):
        return element
    else:
        new_element = ET.Element("unit")
        new_element.append(element)
        return new_element


def srcml_to_code(root: ET.Element) -> str:
    unit_element = _embed_element_into_unit(root)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as xml_file:
        element_tree = ET.ElementTree(unit_element)
        element_tree.write(xml_file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".h") as header_file:
            cmd = f"srcml -l C++ {xml_file.name} --xml-encoding utf-8 --src-encoding utf-8  -o {header_file.name}"
            # print(f"{cmd=}")
            try:
                _COUNT_SRCML_CALLS.ping()
                subprocess.check_call(cmd, shell=True)
                code_bytes = header_file.read()
            except subprocess.CalledProcessError as e:
                print(f"srcml_to_code, error: {e}")
                raise
            finally:
                os.remove(header_file.name)
                os.remove(xml_file.name)

    code_str = code_bytes.decode("utf-8")
    return code_str


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
            result.name_cpp = parse_name(child)
        elif child_tag == "specifier":
            result.specifiers.append(child.text)
        elif child_tag == "modifier":
            result.modifiers.append(child.text)
        else:
            raise SrcMlException(f"Unexpected tag in parse_type: {child_tag}")

    if len(result.name_cpp) == 0:
        assert previous_decl is not None
        result.name_cpp = previous_decl.cpp_type.name_cpp

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
            result.name_cpp = child.text
        elif child_tag == "init":
            expr_child = child_with_tag(child, "expr")
            result.init_cpp = srcml_to_code(expr_child)
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

    if len(result.decl.name_cpp) == 0:
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
            result.name_cpp = parse_name(child)
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


def srcml_to_str(root: ET.Element):
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    return xmlstr


def srcml_to_file(root: ET.Element, filename: str):
    element_tree = ET.ElementTree(root)
    element_tree.write(filename, encoding="utf-8")


def clean_tag(tag_name: str) -> str:
    return tag_name.replace("{http://www.srcML.org/srcML/src}", "")

