"""SrcmlXmlWrapper is a wrapper around the nodes in the xml tree produced by srcml"""

from __future__ import annotations
import inspect
import logging
import sys
import traceback
import yaml  # type: ignore
from srcmlcpp.internal import xmlplain
from dataclasses import dataclass
from typing import Optional, List, Iterable, Callable, Tuple
from xml.etree import ElementTree as ET

from codemanip.code_position import CodePosition
from codemanip import code_utils

from srcmlcpp.internal import srcml_caller
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.internal import srcml_caller, srcml_utils
from srcmlcpp.srcml_exception import SrcMlException


class SrcMlExceptionDetailed(SrcMlException):
    def __init__(self, current_element: SrcmlXmlWrapper, additional_message: str) -> None:
        message = current_element._format_message(additional_message)
        super().__init__(message)


def _get_python_call_info() -> Tuple[str, str]:
    stack_lines = traceback.format_stack()
    error_line = stack_lines[-4]
    frame = inspect.currentframe()  # type: ignore
    if frame is not None:
        caller_function_name = inspect.getframeinfo(frame.f_back.f_back.f_back).function  # type: ignore
    else:
        caller_function_name = ""
    return caller_function_name, error_line


def show_python_callstack(python_error_line: str) -> str:
    return f"""
            Python call stack info:
    {code_utils.indent_code(python_error_line, 4)}
    """


def emit_warning_if_not_quiet(options: SrcmlOptions, message: str) -> None:
    if options.flag_quiet:
        return
    in_pytest = "pytest" in sys.modules
    if in_pytest:
        logging.warning(message)
    else:
        print("Warning: " + message, file=sys.stderr)


@dataclass
class _CodeContextWithCaret:
    """
    Given a extract of the code, and positions in this code, returns a string that highlight
    this position with a caret "^"

    For example:

            Widget widgets[2];
            ^
    """

    concerned_code_lines: List[str]
    start: Optional[CodePosition] = None
    end: Optional[CodePosition] = None

    def __str__(self) -> str:
        msg = ""
        for i, line in enumerate(self.concerned_code_lines):
            msg += line + "\n"
            if self.start is not None:
                if i == self.start.line:
                    nb_spaces = self.start.column - 1
                    if nb_spaces < 0:
                        nb_spaces = 0
                    msg += " " * nb_spaces + "^" + "\n"
        return msg


class SrcmlXmlWrapper:
    """A wrapper around the nodes in the xml tree produced by srcml"""

    # Misc options: in this class, we only use the encoding
    options: SrcmlOptions
    # the xml tree created by srcML
    srcml_xml: ET.Element
    # the filename from which this tree was parsed
    filename: Optional[str] = None
    # the parent of this of node (will be None for the root, which has a tag "unit")
    parent: Optional[SrcmlXmlWrapper]

    def __init__(
        self, options: SrcmlOptions, srcml_xml: ET.Element, parent: Optional[SrcmlXmlWrapper], filename: Optional[str]
    ) -> None:
        """Create a wrapper from an xml sub node
        :param options:  the options
        :param srcml_xml: the xml node which will be wrapped
        :param parent: the parent
        :param filename: the name of the file from which this node was extracted
        """

        self.options = options
        self.srcml_xml = srcml_xml

        # param sanity check
        if filename is not None:
            if len(filename) == 0:
                self.raise_exception("filename params must either be `None` or non empty!")

        if filename is None and parent is not None:
            filename = parent.filename

        self.parent = parent
        self.filename = filename

    def tag(self) -> str:
        """The xml tag
        https://www.tutorialspoint.com/xml/xml_tags.htm"""
        assert self.srcml_xml.tag is not None
        return srcml_utils.clean_tag_or_attrib(self.srcml_xml.tag)

    def has_text(self):
        return self.srcml_xml.text is not None

    def text(self) -> Optional[str]:
        """Text part of the xml element"""
        return self.srcml_xml.text

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
        """Gets the attribute value if present"""
        if attr_name in self.srcml_xml.attrib:
            return self.srcml_xml.attrib[attr_name]
        else:
            return None

    def start(self) -> CodePosition:
        """Start position in the C++ code"""
        start = srcml_utils.element_start_position(self.srcml_xml)
        return CodePosition(-1, -1) if start is None else start

    def end(self) -> CodePosition:
        """End position in the C++ code"""
        end = srcml_utils.element_end_position(self.srcml_xml)
        return CodePosition(-1, -1) if end is None else end

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
        """Save to file as xml"""
        srcml_utils.srcml_to_file(self.options.encoding, self.srcml_xml, filename)

    def children_iterable(self) -> Iterable[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them. Returns an iterable"""
        for child_xml in self.srcml_xml:
            child_wrapper = SrcmlXmlWrapper(self.options, child_xml, self, None)
            yield child_wrapper

    def children(self) -> List[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them"""
        r = []
        for child_xml in self.srcml_xml:
            r.append(SrcmlXmlWrapper(self.options, child_xml, self, None))
        return r

    def children_with_tag(self, tag: str) -> List[SrcmlXmlWrapper]:
        """Extract the xml sub nodes and wraps them"""
        children = self.children()

        r = list(filter(lambda child: child.tag() == tag, children))
        return r

    def depth(self) -> int:
        """The depth of this node, i.e how many parents it has"""
        depth = 0
        current = self
        while current.parent is not None:
            depth += 1
            current = current.parent

        return depth

    def visit_xml_breadth_first(self, xml_visitor_function: SrcmlXmVisitorFunction) -> None:
        """Visits all the elements, and run the given function on them.
        Runs the visitor on the parent first, then on its children
        """
        xml_visitor_function(self)
        for child in self.children():
            child.visit_xml_breadth_first(xml_visitor_function)

    def visit_xml_depth_first(self, xml_visitor_function: SrcmlXmVisitorFunction) -> None:
        """Visits all the elements, and run the given function on them.
        Runs the visitor on the children first, then on their parent
        """
        for child in self.children():
            child.visit_xml_depth_first(xml_visitor_function)
        xml_visitor_function(self)

    def raise_exception(self, message: str) -> None:
        """raises a SrcmlException which will display the message with a context
        that gives the location of this element in the code"""
        raise SrcMlExceptionDetailed(self, message)

    def emit_warning(self, message) -> None:
        """emits a warning which will display the message with a context
        that gives the location of this element in the code"""
        self.emit_message(message, "Warning")

    def emit_info(self, message) -> None:
        """emit an info"""
        self.emit_message(message, "Info")

    def emit_message(self, message, message_header: str) -> None:
        """emit a message"""
        message = self._format_message(message, message_header)
        emit_warning_if_not_quiet(self.options, message)

    def message_detailed(self, message: str, message_header: str = "Warning") -> str:
        r = self._format_message(message, message_header=message_header)
        return r

    def _show_element_info(self) -> str:
        element_tag = self.tag()
        concerned_code = self.str_code_context_with_caret()
        message = f"""
        While parsing a "{element_tag}", corresponding to this C++ code:
        {self.str_code_location()}
{code_utils.indent_code(concerned_code, 12)}
        """
        return message

    def _format_message(self, additional_message: str, message_header: str = "Warning") -> str:

        message = ""

        message += self._show_element_info()

        if self.options.flag_show_python_callstack:
            python_caller_function_name, python_error_line = _get_python_call_info()
            message += show_python_callstack(python_error_line)

        if len(additional_message) > 0:
            message = (
                code_utils.unindent_code(additional_message, flag_strip_empty_lines=True)
                + "\n"
                + code_utils.unindent_code(message, flag_strip_empty_lines=True)
            )

        message = message_header + ": " + message

        return message

    def str_code_context_with_caret(self) -> str:
        from srcmlcpp import srcmlcpp_main

        full_code = srcmlcpp_main._get_cached_file_code(self.filename)

        context: _CodeContextWithCaret

        if len(full_code) > 0:
            full_code_lines = [""] + full_code.split("\n")

            start = self.start()
            end = self.end()
            if start.line >= 0 and end.line >= 0 and len(full_code) > 0:
                concerned_lines = full_code_lines[start.line : end.line + 1]
                new_start = CodePosition(0, start.column)
                new_end = CodePosition(
                    end.line - start.line,
                    end.column,
                )
                context = _CodeContextWithCaret(concerned_lines, new_start, new_end)
            else:
                context = _CodeContextWithCaret([], CodePosition(), CodePosition())
        else:
            original_code = self.str_code_verbatim()
            context = _CodeContextWithCaret(original_code.split("\n"), start, end)

        r = str(context)
        return r

    def str_code_location(self) -> str:
        if self.filename is None:
            header_filename = "Position"
        else:
            header_filename = self.filename

        start = self.start()
        if start.line >= 0:
            return f"{header_filename}:{start.line}:{start.column}"
        else:
            return f"{header_filename}"


# This defines the type of a function that will visit all the children
SrcmlXmVisitorFunction = Callable[[SrcmlXmlWrapper], None]
