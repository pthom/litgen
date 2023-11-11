"""
Some utilities for srcml

This module *must* not depend on srcml_types!
"""
from __future__ import annotations
import logging
import os
from typing import Any, Optional
from xml.dom import minidom
from xml.etree import ElementTree as ET  # noqa

from codemanip.code_position import CodePosition


def _element_position(element: ET.Element, start_or_end: str) -> Optional[CodePosition]:
    r = None
    for key, value in element.attrib.items():
        if clean_tag_or_attrib(key) == start_or_end:
            r = CodePosition.from_string(value)
    return r


def element_start_position(element: ET.Element) -> Optional[CodePosition]:
    return _element_position(element, "start")


def element_end_position(element: ET.Element) -> Optional[CodePosition]:
    return _element_position(element, "end")


def copy_element_end_position(element_src: ET.Element, element_dst: ET.Element) -> None:
    for key, value in element_src.attrib.items():
        if clean_tag_or_attrib(key) == "end":
            end_position = value
            element_dst.attrib[key] = end_position


def children_with_tag(element: ET.Element, tag: str) -> list[ET.Element]:
    r = []
    for child in element:
        child_tag = clean_tag_or_attrib(child.tag)
        if child_tag == tag:
            r.append(child)
    return r


def child_with_tag(element: ET.Element, tag: str) -> Optional[ET.Element]:
    children = children_with_tag(element, tag)
    if len(children) == 0:
        return None
    elif len(children) > 1:
        message = f'child_with_tag: found more than one child with tag "{tag}" (found {len(children)})'
        logging.debug(message)
        return None
    else:
        return children[0]


def srcml_to_str(element: ET.Element, bare: bool = False) -> str:
    xmlstr_raw = ET.tostring(element, encoding="unicode")
    if bare:
        return xmlstr_raw

    try:
        xmlstr: str = minidom.parseString(ET.tostring(element)).toprettyxml(indent="   ")
    except Exception:
        xmlstr = xmlstr_raw

    return xmlstr


def srcml_write_to_file(encoding: str, root: ET.Element, filename: str) -> None:
    element_tree = ET.ElementTree(root)
    element_tree.write(filename, encoding=encoding)


def clean_tag_or_attrib(tag_name: str) -> str:
    if tag_name.startswith("{"):
        assert "}" in tag_name
        pos = tag_name.index("}") + 1
        tag_name = tag_name[pos:]
    tag_name = tag_name.replace("ns0:", "")
    tag_name = tag_name.replace("ns1:", "")
    return tag_name


def str_or_empty(what: Any) -> str:
    return "" if what is None else str(what)


def _extract_interesting_text(element: ET.Element) -> str:
    if element.text is None:
        return ""
    text = element.text.replace("\n", " ").strip()
    if text == ";":
        text = ""
    return text


def _extract_interesting_tail(element: ET.Element) -> str:
    if element.tail is None:
        return ""
    text = element.tail.replace("\n", " ").strip()
    if text == ";":
        text = ""
    return text


_PREVIOUS_INFO_POSITION = ""


def _info_element_position(element: ET.Element) -> str:
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


def srcml_to_str_readable(srcml_element: ET.Element, level: int = 0) -> str:
    indent_str = "    " * level

    msg: str
    msg = indent_str + clean_tag_or_attrib(srcml_element.tag)
    text = _extract_interesting_text(srcml_element)
    if len(text) > 0:
        msg += f' text="{text}"'

    info_position = _info_element_position(srcml_element)
    if len(info_position) > 0:
        msg += " " * (60 - len(msg)) + info_position
    msg += "\n"

    for child in srcml_element:
        msg += srcml_to_str_readable(child, level + 1)
    return msg


def check_for_file_in_current_hierarchy(filename: str) -> bool:
    """Checks whether a file with the given name exists in the current folder or any of its parent directories."""
    current_dir = os.getcwd()
    while True:
        file_path = os.path.join(current_dir, filename)
        if os.path.isfile(file_path):
            return True
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached the root directory without finding the file
            return False
        current_dir = parent_dir
