from typing import Tuple, List, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom

from srcml_caller import srcml_to_code
from litgen.internal.srcml import srcml_utils, srcml_caller
from litgen.internal.srcml.srcml_types import CodePosition
import logging


def _element_position(element: ET.Element, start_or_end: str) -> CodePosition:
    r = None
    for key, value in element.attrib.items():
        if clean_tag_or_attrib(key) == start_or_end:
            r = CodePosition.from_string(value)
    return r


def element_start_position(element: ET.Element) -> CodePosition:
    return _element_position(element, "start")


def element_end_position(element: ET.Element) -> CodePosition:
    return _element_position(element, "end")


def copy_element_end_position(element_src: ET.Element, element_dst: ET.Element):
    for key, value in element_src.attrib.items():
        if clean_tag_or_attrib(key) == "end":
            end_position = value
            element_dst.attrib[key] = end_position


def element_name(element: ET.Element) -> str:
    assert clean_tag_or_attrib(element.tag) == "name"
    is_composed = (element.text is None)
    name = srcml_to_code(element).strip() if is_composed else element.text
    return name


def children_with_tag(element: ET.Element, tag: str) -> List[ET.Element]:
    r = []
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == tag:
            r.append(child)
    return r


def first_code_element_with_tag(code: str, tag: str, dump_positions: bool = True) -> ET.Element:
    """
    Utility for tests: extracts the first xml element of type "decl_stmt"
    """
    root = srcml_caller.code_to_srcml(code, dump_positions)
    return child_with_tag(root, tag)


def child_with_tag(element: ET.Element, tag: str) -> ET.Element:
    children = children_with_tag(element, tag)
    if len(children) == 0:
        tags_strs = map(lambda c: '"' + clean_tag_or_attrib(c.tag) + '"', element)
        tags_str = ", ".join(tags_strs)
        message = f'child_with_tag: did not find child with tag "{tag}"  (found [{tags_str}])'
        logging.error(message)
        raise LookupError(message)
    elif len(children) > 1:
        message = f'child_with_tag: found more than one child with tag "{tag}" (found {len(children)})'
        logging.error(message)
        raise LookupError(message)
    return  children[0]


def srcml_to_str(element: ET.Element, bare = False):
    xmlstr_raw = ET.tostring(element, encoding="unicode")
    if bare:
        return xmlstr_raw

    try:
        xmlstr = minidom.parseString(ET.tostring(element)).toprettyxml(indent="   ")
    except Exception as e:
        xmlstr = xmlstr_raw

    return xmlstr


def srcml_to_file(encoding: str, root: ET.Element, filename: str):
    element_tree = ET.ElementTree(root)
    element_tree.write(filename, encoding=encoding)


def clean_tag_or_attrib(tag_name: str) -> str:
    if tag_name.startswith("{"):
        assert("}") in tag_name
        pos = tag_name.index("}") + 1
        tag_name = tag_name[ pos : ]
    tag_name = tag_name.replace("ns0:", "")
    tag_name = tag_name.replace("ns1:", "")
    return tag_name


def str_none_empty(what: Any):
    return "" if what is None else str(what)


def _extract_interesting_text(element: ET.Element):
    if element.text is None:
        return ""
    text = element.text.replace("\n", " ").strip()
    if text == ";":
        text = ""
    return text

def _extract_interesting_tail(element: ET.Element):
    if element.tail is None:
        return ""
    text = element.tail.replace("\n", " ").strip()
    if text == ";":
        text = ""
    return text


_PREVIOUS_INFO_POSITION = ""


def _info_element_position(element: ET.Element):
    global _PREVIOUS_INFO_POSITION
    start, end = element_start_position(element), element_end_position(element)
    if start is None or end is None:
        return ""
    if start.line == end.line:
        r = f"line  {start.line}"
    else:
        r = f"lines {start.line}-{end.line}"

    if r != _PREVIOUS_INFO_POSITION:
        _PREVIOUS_INFO_POSITION = r
        return r
    else:
        return ""


def srcml_to_str_readable(srcml_element: ET.Element, level = 0) -> str:
    indent_str = "    " * level
    msg = indent_str + clean_tag_or_attrib(srcml_element.tag)
    text = _extract_interesting_text(srcml_element)
    tail = _extract_interesting_tail(srcml_element)
    if len(text) > 0:
        msg += f' text="{text}"'
    # if len(tail) > 0:
    #     msg += f' tail="{tail}"'

    info_position = _info_element_position(srcml_element)
    if len(info_position) > 0:
        msg += " " * (60 - len(msg)) + info_position
    msg += "\n"

    for child in srcml_element:
        msg += srcml_to_str_readable(child, level + 1)
    return msg
