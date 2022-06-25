from __future__ import annotations
import yaml  # type: ignore
from srcmlcpp.internal import xmlplain
from typing import Optional, List, Iterable
from xml.etree import ElementTree as ET

from codemanip.code_position import CodePosition

from srcmlcpp.internal import srcml_caller
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.internal import srcml_caller, srcml_utils
from srcmlcpp.srcml_exception import SrcMlException


class SrcmlXmlWrapper:
    """A wrapper around the xml tree produced by srcml"""

    # Misc options: in this class, we only use the encoding
    options: SrcmlOptions
    # the xml tree created by srcML
    srcml_xml: ET.Element
    # the filename from which this tree was parsed
    filename: Optional[str] = None

    def __init__(self, options: SrcmlOptions, srcml_xml: ET.Element, filename: Optional[str]) -> None:
        """Create a wrapper from an xml sub node"""
        self.options = options
        self.srcml_xml = srcml_xml
        self.filename = filename
        if filename is not None:
            if len(filename) == 0:
                raise SrcMlException("filename params must either be `None` or non empty!")

    def tag(self) -> str:
        assert self.srcml_xml.tag is not None
        return srcml_utils.clean_tag_or_attrib(self.srcml_xml.tag)

    def text(self) -> Optional[str]:
        """Text part of the xml element"""
        return self.srcml_xml.text

    def start(self) -> CodePosition:
        """Start position in the C++ code"""
        start = srcml_utils.element_start_position(self.srcml_xml)
        return CodePosition(-1, -1) if start is None else start

    def end(self) -> CodePosition:
        """End position in the C++ code"""
        end = srcml_utils.element_end_position(self.srcml_xml)
        return CodePosition(-1, -1) if end is None else end

    def has_name(self) -> bool:
        name_children = srcml_utils.children_with_tag(self.srcml_xml, "name")
        return len(name_children) == 1

    def name_code(self) -> Optional[str]:
        """Returns the C++ code corresponding to the name extracted from the srcML xml tree.

        * In simple cases, it will be a simple text extraction, for example with the code:
            int a = 10;
          The decl name node will look like
            <name>a</name>

        * Sometimes, we will need to call srcml to reconstruct the code.
          For example, with the code:
            int* a[10];
          The decl name node will look like
               <name>
                    <name>a</name>
                    <index>[
                        <expr>
                            <literal type="number">10</literal>
                        </expr>]
                    </index>
                </name>
        """
        if not self.has_name():
            return None
        name_element = srcml_utils.child_with_tag(self.srcml_xml, "name")
        assert name_element is not None
        if name_element.text is not None:
            return name_element.text
        else:
            return srcml_caller.srcml_to_code(name_element)

    def attribute_value(self, attr_name: str) -> Optional[str]:
        if attr_name in self.srcml_xml.attrib:
            return self.srcml_xml.attrib[attr_name]
        else:
            return None

    def str_code_verbatim(self) -> str:
        """Return the exact C++ code from which this xml node was constructed by calling the executable srcml"""
        r = srcml_caller.srcml_to_code(self.srcml_xml, encoding=self.options.encoding)
        return r

    def str_xml(self, beautify: bool = True) -> str:
        """An xml string representing the content of the xml node"""
        r = srcml_utils.srcml_to_str(self.srcml_xml, bare=not beautify)
        return r

    def _str_simplified_yaml(self) -> str:
        """Return the xml tree formatted in a yaml inspired format. Should be deprecated"""
        return srcml_utils.srcml_to_str_readable(self.srcml_xml)

    def str_yaml(self) -> str:
        """A yaml representation of the xml tree.
        No guaranty is made that it a roundtrip xml->yaml->xml is possible"""
        xml_str = self.str_xml(beautify=False)  # type: ignore
        root = xmlplain.xml_to_obj(xml_str, self.options.encoding)  # type: ignore
        yaml_str: str = yaml.safe_dump(root, default_flow_style=False, allow_unicode=True)  # type: ignore
        return yaml_str

    def to_file(self, filename: str) -> None:
        srcml_utils.srcml_to_file(self.options.encoding, self.srcml_xml, filename)

    def children(self) -> Iterable[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them"""
        for child_xml in self.srcml_xml:
            child_wrapper = SrcmlXmlWrapper(self.options, child_xml, self.filename)
            yield child_wrapper

    def children_with_tag(self, tag: str) -> List[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them"""
        children_xml = srcml_utils.children_with_tag(self.srcml_xml, tag)
        r: List[SrcmlXmlWrapper] = []
        for child_xml in children_xml:
            r.append(SrcmlXmlWrapper(self.options, child_xml, self.filename))
        return r

    def child_with_tag(self, tag: str) -> Optional[SrcmlXmlWrapper]:
        child_xml = srcml_utils.child_with_tag(self.srcml_xml, tag)
        if child_xml is None:
            return None
        r = SrcmlXmlWrapper(self.options, child_xml, self.filename)
        return r
