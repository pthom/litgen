from __future__ import annotations
import yaml  # type: ignore
from srcmlcpp.internal import xmlplain
from typing import Optional, List
from xml.etree import ElementTree as ET

from codemanip.code_position import CodePosition

from srcmlcpp.internal import srcml_caller
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.internal import srcml_caller, srcml_utils, srcml_comments


class SrcmlXmlWrapper:
    """A wrapper around the xml tree produced by srcml"""

    # Misc options: in this class, we only use the encoding
    options: SrcmlOptions
    # the xml tree created by srcML
    srcml_xml: ET.Element
    # the filename from which this tree was parsed
    filename: Optional[str] = None

    def __init__(self) -> None:
        """Do not construct this class directly, use from_code and from_srcml_xml"""
        pass

    @staticmethod
    def from_code(
        options: SrcmlOptions, cpp_code: Optional[str] = None, filename: Optional[str] = None
    ) -> SrcmlXmlWrapper:
        """Create a wrapper from c++ code

        Note:
            * if `cpp_code` is not empty, the code will be taken from it.
              In this case, the `filename` param will still be used to display code source position in warning messages.
              This can be used when you need to preprocess the code before parsing it.
            * if `code`is empty, the code will be read from `filename`
        """
        self = SrcmlXmlWrapper()
        self.options = options

        self.filename = filename

        if cpp_code is None:
            if self.filename is None:
                raise ValueError("Either cpp_code or filename needs to be specified!")
            assert filename is not None  # make mypy happy
            with open(filename, "r", encoding=options.encoding) as f:
                cpp_code = f.read()

        if options.code_preprocess_function is not None:
            cpp_code = options.code_preprocess_function(cpp_code)

        if options.preserve_empty_lines:
            cpp_code = srcml_comments.mark_empty_lines(cpp_code)

        self.srcml_xml = srcml_caller.code_to_srcml(
            cpp_code, dump_positions=self.options.srcml_dump_positions, encoding=options.encoding
        )

        return self

    @staticmethod
    def from_srcml_xml(options: SrcmlOptions, srcml_xml: ET.Element, filename: Optional[str] = None) -> SrcmlXmlWrapper:
        """Create a wrapper from an xml sub node"""
        self = SrcmlXmlWrapper()
        self.options = options
        self.srcml_xml = srcml_xml
        self.filename = filename
        return self

    def tag(self) -> Optional[str]:
        tag = self.srcml_xml.tag
        if tag is None:
            return None
        tag_clean = srcml_utils.clean_tag_or_attrib(tag)
        return tag_clean

    def start_position(self) -> Optional[CodePosition]:
        """start position of the element in the code (line and column numbering starts at 1)"""
        r = srcml_utils.element_start_position(self.srcml_xml)
        return r

    def end_position(self) -> Optional[CodePosition]:
        """end position of the element in the code (line and column numbering starts at 1)"""
        r = srcml_utils.element_end_position(self.srcml_xml)
        return r

    def children_with_tag(self, tag: str) -> List[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them"""
        children_xml = srcml_utils.children_with_tag(self.srcml_xml, tag)
        r: List[SrcmlXmlWrapper] = []
        for child_xml in children_xml:
            r.append(SrcmlXmlWrapper.from_srcml_xml(self.options, child_xml))
        return r

    def child_with_tag(self, tag: str) -> Optional[SrcmlXmlWrapper]:
        child_xml = srcml_utils.child_with_tag(self.srcml_xml, tag)
        if child_xml is None:
            return None
        r = SrcmlXmlWrapper.from_srcml_xml(self.options, child_xml)
        return r

    def code_verbatim(self) -> str:
        """An exact (verbatim) copy of the code from which this object was created"""
        r = srcml_caller.srcml_to_code(self.srcml_xml, encoding=self.options.encoding)
        return r

    def as_xml_str(self, beautify: bool = True) -> str:
        """An xml string representing the content of self.srcml_tree"""
        r = srcml_utils.srcml_to_str(self.srcml_xml, bare=not beautify)
        return r

    def as_yaml(self) -> str:
        """A yaml representation of the xml tree.
        No guaranty is made that it a roundtrip xml->yaml->xml is possible"""
        xml_str = self.as_xml_str(beautify=False)  # type: ignore
        root = xmlplain.xml_to_obj(xml_str, self.options.encoding)  # type: ignore
        yaml_str: str = yaml.safe_dump(root, default_flow_style=False, allow_unicode=True)  # type: ignore
        return yaml_str

    def to_file(self, filename: str) -> None:
        srcml_utils.srcml_to_file(self.options.encoding, self.srcml_xml, filename)
