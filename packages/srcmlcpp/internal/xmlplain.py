# type: ignore

from __future__ import print_function

"""
xmlplain: transform a xml tree into yaml

from https://github.com/guillon/xmlplain
Thanks to Christophe Guillon !
"""

#!/usr/bin/env python
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>
#

"""
XML as plain object module.

This module is a set of utility functions for parsing XML input
into plain list/dict/string types.

These plain XML objects in turn can be emitted through YAML
for instance as bare YAML without python objects.

The motivating usage is to dump XML to YAML, manually edit
files as YAML, and emit XML output back.

The original XML file is supposed to be preserved except
for comments and if requested spaces between elements.

Note that there are alternative modules with nearly the same
functionality, but none of them both provide simple plain objects
and preserve the initial XML content for non structured XML.

XML namespaces are preserved for attributes/elements
and re-emitted as is.

WARNING: from the original XML documents, DTD specification,
XML comments and processing entities will be discarded.
Also system external entities are not allowed and will
generate an exception.
If one needs some of these features, it's probably
not the right usage for this module. Fill an issue if unsure.

:Example:
    >>> import xmlplain, sys

    >>> _ = sys.stdout.write(open("tests/example-1.xml").read())
    <example>
      <doc>This is an example for xmlobj documentation. </doc>
      <content version="beta">
        <kind>document</kind>
        <class>example</class>
        <structured/>
        <elements>
          <item>Elt 1</item>
          <doc>Elt 2</doc>
          <item>Elt 3</item>
          <doc>Elt 4</doc>
        </elements>
      </content>
    </example>

    >>> root = xmlplain.xml_to_obj(open("tests/example-1.xml"), strip_space=True, fold_dict=True)
    >>> xmlplain.obj_to_yaml(root, sys.stdout)
    example:
      doc: 'This is an example for xmlobj documentation. '
      content:
        '@version': beta
        kind: document
        class: example
        structured: ''
        elements:
        - item: Elt 1
        - doc: Elt 2
        - item: Elt 3
        - doc: Elt 4

    >>> xmlplain.xml_from_obj(root, sys.stdout)
    <?xml version="1.0" encoding="UTF-8"?>
    <example>
      <doc>This is an example for xmlobj documentation. </doc>
      <content version="beta">
        <kind>document</kind>
        <class>example</class>
        <structured></structured>
        <elements>
          <item>Elt 1</item>
          <doc>Elt 2</doc>
          <item>Elt 3</item>
          <doc>Elt 4</doc>
        </elements>
      </content>
    </example>

"""


__version__ = "1.6.0"

import yaml, sys, xml, io
import contextlib
import xml.sax.saxutils

try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover # python 2.6 only
    from ordereddict import OrderedDict


def xml_to_events(inf, handler=None, encoding="UTF-8", process_content=None):
    """
    Generates XML events tuples from the input stream.

    The generated events consist of pairs: (type, value)
    where type is a single char identifier for the event and
    value is a variable length tuple.
    Events correspond to xml.sax events with the exception that
    attributes are generated as events instead of being part of
    the start element event.
    The XML stresm is parsed with xml.sax.make_parser().

    :param inf: input stream file or string or bytestring
    :param handler: events receiver implementing the append() method or None,
      in which case a new list will be generated
    :param encoding: encoding used whebn the input is a bytes string
    :param process_content: a function to apply to the cdata content (str for
        python3 or unicode for python2) after the XML reader content generation

    :return: returns the handler or the generated list

    The defined XML events tuples in this module are:

    - ("[", ("",)) for the document start
    - ("]", ("",)) for the document end
    - ("<", (elt_name,)) for an element start
    - (">", (elt_name,)) for an element end
    - ("@", (attr_name, attr_value)) for an attribute associated to the
      last start element
    - ("|", (content,)) for a CDATA string content
    - ("#", (whitespace,)) for an ignorable whitespace string

    .. seealso: xml_from_events(), xml.sax.parse()
    """

    class EventGenerator(xml.sax.ContentHandler):
        def __init__(self, handler, process_content=None):
            self.handler = handler
            self.process_content = process_content

        def startElement(self, name, attrs):
            self.handler.append(("<", (name,)))
            # Enforce a stable order as sax attributes are unordered
            for attr in sorted(attrs.keys()):
                handler.append(("@", (attr, attrs[attr])))

        def endElement(self, name):
            self.handler.append((">", (name,)))

        def startDocument(self):
            self.handler.append(("[", ("",)))

        def endDocument(self):
            self.handler.append(("]", ("",)))

        def characters(self, content):
            if self.process_content != None:
                content = self.process_content(content)
            self.handler.append(("|", (content,)))

    class EntityResolver(xml.sax.handler.EntityResolver):
        def resolveEntity(self, publicId, systemId):
            raise Exception("invalid system entity found: (%s, %s)" % (publicId, systemId))

    if handler == None:
        handler = []
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, False)
    parser.setFeature(xml.sax.handler.feature_namespace_prefixes, False)
    parser.setFeature(xml.sax.handler.feature_external_ges, True)
    parser.setEntityResolver(EntityResolver())
    parser.setContentHandler(EventGenerator(handler, process_content=process_content))
    if sys.version_info[0] == 2 and isinstance(inf, unicode):
        inf = inf.encode(encoding)
    if sys.version_info[0] >= 3 and isinstance(inf, str):
        inf = inf.encode(encoding)
    if isinstance(inf, bytes):
        src = xml.sax.xmlreader.InputSource()
        src.setEncoding(encoding)
        src.setByteStream(io.BytesIO(inf))
        parser.parse(src)
    else:
        parser.parse(inf)
    return handler


def xml_from_events(events, outf=None, encoding="UTF-8", process_content=None):
    """
    Outputs the XML document from the events tuples.

    From the given events tuples lists as specified in xml_to_events(),
    generated a well formed XML document.
    The XML output is generated through xml.saxutils.XMLGenerator().

    :param events: events tuples list or iterator
    :param outf: output file stream or None for bytestring output
    :param encoding: output encoding
    :param process_content: a function to apply to the cdata content (str for
        python3 or unicode for python2) before being processed by the XML
        writer
    :return: created byte string when outf if None

    .. note: unknown events types are ignored
    .. seealso: xml_to_events(), xml.sax.saxutils.XMLGenerator()
    """

    class SaxGenerator:
        def __init__(self, sax_receiver, process_content=None):
            self.sax_receiver = sax_receiver
            self.process_content = process_content

        def append(self, evt):
            kind, value = evt
            if kind == "[":
                self.sax_receiver.startDocument()
                self.start = None
                return
            if kind == "@":
                self.start[1][value[0]] = value[1]
                return
            if self.start != None:
                self.sax_receiver.startElement(*self.start)
                self.start = None
            if kind == "]":
                self.sax_receiver.endDocument()
            elif kind == "<":
                self.start = (value[0], OrderedDict())
            elif kind == ">":
                self.sax_receiver.endElement(value[0])
            elif kind == "|":
                content = value[0]
                if self.process_content != None:
                    content = self.process_content(content)
                self.sax_receiver.characters(content)
            elif kind == "#":
                self.sax_receiver.ignorableWhitespace(value[0])

    class QuotingWriter:
        def __init__(self, parent, encoding):
            self.parent = parent
            self.input_encoding = encoding
            # '\r' must be quoted to &#xd; in the output
            # XMLGenerator() does not, hence we do it there
            self.quoting = [(b"\r", b"&#xd;")]
            self.binary = True
            try:
                self.parent.write(b"")
            except TypeError as e:
                self.binary = False

        def write(self, content):
            assert isinstance(content, bytes)
            for k, v in self.quoting:
                content = content.replace(k, v)
            if not self.binary:
                content = content.decode(self.input_encoding)
            return self.parent.write(content)

    getvalue = None
    if outf == None:
        outf = io.BytesIO()
        getvalue = outf.getvalue
    writer = QuotingWriter(outf, encoding=encoding)
    generator = xml.sax.saxutils.XMLGenerator(writer, encoding=encoding)
    generator = SaxGenerator(generator, process_content=process_content)
    for evt in events:
        generator.append(evt)
    if getvalue:
        return getvalue()


def xml_to_obj(inf, encoding="UTF-8", strip_space=False, fold_dict=False, process_content=None):
    """
    Generate an plain object representation from the XML input.

    The representation consists of lists of plain
    elements which are either XML elements as dict
    { elt_name: children_list } or XML CDATA text contents as
    plain strings.
    This plain object for a XML document can be emitted to
    YAML for instance with no python dependency.

    When the 'fold' option is given, an elements list may be
    simplified into a multiple key ordered dict or a single text content.
    Note that in this case, some Ordered dict python objects may be generated,
    one should then use the obj_to_yaml() method in order to get a bare
    YAML output.

    When the 'strip_space' option is given, non-leaf text content
    are striped, this is in most case safe when managing structured
    XML, though, note that this change your XML document content.
    Generally one would use this in conjonction with pretty=true
    when emitting back the object to XML with xml_from_obj().

    :param inf: input stream file or string or bytestring
    :param encoding: encoding used when the input is bytes string
    :param strip_space: strip spaces from non-leaf text content
    :param fold_dict: optimized unambiguous lists of dict into ordered dicts
    :param process_content: a function to apply to the cdata content (str for
        python3 or unicode for python2) after the XML reader content generation

    :return: the root of the generated plain object, actually a single key dict

    :Example:

    >>> import xmlplain, yaml, sys
    >>> root = xmlplain.xml_to_obj(open("tests/example-1.xml"), strip_space=True)
    >>> yaml.safe_dump(root, sys.stdout, default_flow_style=False, allow_unicode=True)
    example:
    - doc: 'This is an example for xmlobj documentation. '
    - content:
      - '@version': beta
      - kind: document
      - class: example
      - structured: ''
      - elements:
        - item: Elt 1
        - doc: Elt 2
        - item: Elt 3
        - doc: Elt 4

    >>> root = xmlplain.xml_to_obj(open("tests/example-1.xml"), strip_space=True, fold_dict=True)
    >>> xmlplain.obj_to_yaml(root, sys.stdout)
    example:
      doc: 'This is an example for xmlobj documentation. '
      content:
        '@version': beta
        kind: document
        class: example
        structured: ''
        elements:
        - item: Elt 1
        - doc: Elt 2
        - item: Elt 3
        - doc: Elt 4

    .. seealso: xml_from_obj()
    """

    class ObjGenerator:
        def __init__(self, strip_space=False, fold_dict=False):
            self.value = None
            self.strip_space = strip_space
            self.fold_dict = fold_dict

        def get_value(self):
            return self.value

        def strip_space_elts(self, elts):
            # Only strip space when not a leaf
            if len(elts) <= 1:
                return elts
            elts = [e for e in [s.strip() if not isinstance(s, dict) else s for s in elts] if e != ""]
            return elts

        def fold_dict_elts(self, elts):
            if len(elts) <= 1:
                return elts
            # Simplify into an OrderedDict if there is no mixed text and no key duplicates
            keys = ["#" if not isinstance(e, dict) else list(e.keys())[0] for e in elts]
            unique_keys = list(set(keys))
            if len(unique_keys) == len(keys) and "#" not in unique_keys:
                return OrderedDict([list(elt.items())[0] for elt in elts])
            return elts

        def fold_trivial(self, elts):
            if isinstance(elts, list):
                if len(elts) == 0:
                    return ""
                if len(elts) == 1:
                    return elts[0]
            return elts

        def process_children(self):
            name, children = list(self.stack[-1].items())[0]
            children = self.children()
            if self.strip_space:
                children = self.strip_space_elts(children)
            if self.fold_dict:
                children = self.fold_dict_elts(children)
            children = self.fold_trivial(children)
            self.stack[-1][name] = children

        def children(self):
            return list(self.stack[-1].values())[0]

        def push_elt(self, name):
            elt = {name: []}
            self.children().append(elt)
            self.stack.append(elt)

        def pop_elt(self, name):
            self.stack.pop()

        def append_attr(self, name, value):
            self.children().append({"@%s" % name: value})

        def append_content(self, content):
            children = self.children()
            if len(children) > 0 and not isinstance(children[-1], dict):
                children[-1] += content
            else:
                children.append(content)

        def append(self, event):
            kind, value = event
            if kind == "[":
                self.stack = [{"_": []}]
            elif kind == "]":
                self.value = self.children()[0]
            elif kind == "<":
                self.push_elt(value[0])
            elif kind == ">":
                self.process_children()
                self.pop_elt(value[0])
            elif kind == "@":
                self.append_attr(value[0], value[1])
            elif kind == "|":
                self.append_content(value[0])

    return xml_to_events(
        inf,
        ObjGenerator(strip_space=strip_space, fold_dict=fold_dict),
        encoding=encoding,
        process_content=process_content,
    ).get_value()


def events_filter_pretty(events, handler=None, indent="  "):
    """
    Augment an XML event list for pretty printing.

    This is a filter function taking an event stream and returning the
    augmented event stream including ignorable whitespaces for an indented
    pretty print. the generated events stream is still a valid events stream
    suitable for xml_from_events().

    :param events: the input XML events stream
    :param handler: events receiver implementing the append() method or None,
      in which case a new list will be generated
    :param indent: the base indent string, defaults to 2-space indent

    :return: the handler if not None or the newly created events list

    .. seealso: xml_from_event()
    """

    class EventFilterPretty:
        def __init__(self, handler, indent="  "):
            self.handler = handler
            self.indent = indent

        def filter(self, events):
            events = iter(events)
            lookahead = []
            depth = 0
            while True:
                if len(lookahead) == 0:
                    while True:
                        e = next(events, None)
                        if e == None:
                            break
                        lookahead.append(e)
                        if e[0] in [">", "]"]:
                            break
                    if len(lookahead) == 0:
                        break
                kinds = list(next(iter(zip(*lookahead))))
                if kinds[0] == "<" and not "<" in kinds[1:]:
                    if depth > 0:
                        self.handler.append(("#", ("\n",)))
                    self.handler.append(("#", (self.indent * depth,)))
                    while lookahead[0][0] != ">":
                        self.handler.append(lookahead.pop(0))
                    self.handler.append(lookahead.pop(0))
                    if depth == 0:
                        self.handler.append(("#", ("\n",)))
                else:
                    if kinds[0] == "<":
                        if depth > 0:
                            self.handler.append(("#", ("\n",)))
                        self.handler.append(("#", (self.indent * depth,)))
                        self.handler.append(lookahead.pop(0))
                        depth += 1
                    elif kinds[0] == ">":
                        depth -= 1
                        self.handler.append(("#", ("\n",)))
                        self.handler.append(("#", (self.indent * depth,)))
                        self.handler.append(lookahead.pop(0))
                        if depth == 0:
                            self.handler.append(("#", ("\n",)))
                    elif kinds[0] == "|":
                        self.handler.append(("#", ("\n",)))
                        self.handler.append(("#", (self.indent * depth,)))
                        self.handler.append(lookahead.pop(0))
                    else:
                        self.handler.append(lookahead.pop(0))
            assert next(events, None) == None  # assert all events are consummed

    if handler == None:
        handler = []
    EventFilterPretty(handler).filter(events)
    return handler


def events_from_obj(root, handler=None):
    """
    Creates an XML events stream from plain object.

    Generates an XML event stream suitable for xml_from_events() from
    a well formed XML plain object and pass it through the append()
    method to the receiver or to a newly created list.

    :param root: root of the XML plain object
    :param handler: events receiver implementing the append() method or None,
      in which case a new list will be generated

    :return: the handler if not None or the created events list

    .. seealso: xml_from_events()
    """

    class EventGenerator:
        def __init__(self, handler):
            self.handler = handler

        def gen_content(self, token):
            self.handler.append(("|", (token,)))

        def gen_elt(self, name, children):
            self.handler.append(("<", (name,)))
            self.gen_attrs_or_elts(children)
            self.handler.append((">", (name,)))

        def gen_attr(self, name, value):
            self.handler.append(("@", (name, value)))

        def gen_attr_or_elt(self, name, children):
            if name[0] == "@":
                self.gen_attr(name[1:], children)
            else:
                self.gen_elt(name, children)

        def gen_attrs_or_elts(self, elts):
            if isinstance(elts, list):
                for elt in elts:
                    self.gen_attrs_or_elts(elt)
            elif isinstance(elts, dict):
                for name, children in elts.items():
                    self.gen_attr_or_elt(name, children)
            else:
                self.gen_content(elts)

        def generate_from(self, root):
            assert isinstance(root, dict)
            assert len(root.items()) == 1
            (name, children) = list(root.items())[0]
            self.handler.append(("[", ("",)))
            self.gen_elt(name, children)
            self.handler.append(("]", ("",)))

    if handler == None:
        handler = []
    EventGenerator(handler).generate_from(root)
    return handler


def xml_from_obj(root, outf=None, encoding="UTF-8", pretty=True, indent="  ", process_content=None):
    """
    Generate a XML output from a plain object

    Generates to the XML representation for the plain object as
    generated by this module..
    This function does the opposite of xml_to_obj().

    :param root: the root of the plain object
    :param outf: output file stream or None for bytestring output
    :param encoding: the encoding to be used (default to "UTF-8")
    :param pretty: does indentation when True
    :param indent: base indent string (default to 2-space)
    :param process_content: a function to apply to the cdata content (str for
        python3 or unicode for python2) before being processed by the XML
        writer

    :return: created byte string when outf if None

    .. seealso xml_to_obj()
    """
    events = events_from_obj(root)
    if pretty:
        events = events_filter_pretty(events, indent=indent)
    return xml_from_events(events, outf, encoding=encoding, process_content=process_content)


def obj_to_yaml(root, outf=None, encoding="UTF-8", process_string=None):
    """
    Output an XML plain object to yaml.

    Output an object to yaml with some specific
    management for OrderedDict, Strings and Tuples.
    The specific treatment for these objects are
    there in order to preserve the XML ordered structure
    while generating a bare yaml file without any python object.

    Note that reading back the emitted YAML object should be done
    though obj_from_yaml() in order to preserve dict order.

    To be used as an alternative to a bare yaml.dump if one
    needs an editable YAML view of the XML plain object.

    :param root: root of the plain object to dump
    :param outf: output file stream or None for bytestring output
    :param encoding: output bytestring or file stream encoding
    :param process_string: a function to apply to strings (str for
        python3 or unicode for python2) before the YAML writer output

    :return: None or the generated byte string if stream is None
    """

    class LocalDumper(yaml.SafeDumper):
        def dict_representer(self, data):
            return self.represent_dict(data.items())

        def represent_scalar(self, tag, value, style=None):
            if tag == "tag:yaml.org,2002:str":
                if process_string != None:
                    value = process_string(value)
            # force strings with newlines to output as block mode
            if tag == "tag:yaml.org,2002:str" and style != "|" and value.find("\n") >= 0:
                style = "|"
            return yaml.SafeDumper.represent_scalar(self, tag, value, style)

    LocalDumper.add_representer(OrderedDict, LocalDumper.dict_representer)

    return yaml.dump(root, outf, allow_unicode=True, default_flow_style=False, encoding=encoding, Dumper=LocalDumper)


def obj_from_yaml(inf, encoding="UTF-8", process_string=None):
    """
    Read a YAML object, possibly holding a XML plain object.

    Returns the XML plain obj from the YAML stream or string.
    The dicts read from the YAML stream are stored as
    OrderedDict such that the XML plain object elements
    are kept in order.

    :param inf: input YAML file stream or string or bytestring
    :param encoding: encoding of the input when a byte stream or byte string
    :param process_string: a function to apply to strings (str for
        python3 or unicode for python2) after the YAML reader input

    :return: the constructed plain object
    """

    class LocalLoader(yaml.SafeLoader):
        def map_constructor(self, node):
            self.flatten_mapping(node)
            return OrderedDict(self.construct_pairs(node))

        def str_constructor(self, node):
            value = yaml.SafeLoader.construct_yaml_str(self, node)
            encoded = False
            if sys.version_info[0] == 2 and isinstance(value, bytes):
                encoded = True
                value = value.decode("ascii")
            if process_string != None:
                value = process_string(value)
            if encoded:
                value = value.encode("ascii")
            return value

    LocalLoader.add_constructor("tag:yaml.org,2002:map", LocalLoader.map_constructor)
    LocalLoader.add_constructor("tag:yaml.org,2002:str", LocalLoader.str_constructor)

    # Yaml assume utf-8/utf-16 encoding only on reading,
    # hence decode first if the requested encoding is not utf-8
    if encoding.upper != "UTF-8":
        if hasattr(inf, "read"):
            inf = inf.read()
        if isinstance(inf, bytes):
            inf = inf.decode(encoding)
    return yaml.load(inf, Loader=LocalLoader)


if __name__ == "__main__":
    import argparse, sys, os

    if "--doctest" in sys.argv:
        import doctest

        test = doctest.testmod()
        sys.exit(0 if test.failed == 0 else 1)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version="xmlplain version %s (path: %s, python: %s)" % (__version__, __file__, sys.version.split()[0]),
    )
    parser.add_argument("--doctest", action="store_true", help="run documentation tests")
    parser.add_argument("--test", action="store_true", help="run in test mode, filter exceptions")
    parser.add_argument("--string", action="store_true", help="read from or write to string first")
    parser.add_argument("--in-process", nargs=2, help="2 arguments 'str_in' 'str_out' for processing on read")
    parser.add_argument("--out-process", nargs=2, help="2 arguments 'str_in' 'str_out' for processing on write")
    parser.add_argument("--in-encoding", default="UTF-8", help="encoding for input")
    parser.add_argument("--out-encoding", default="UTF-8", help="encoding for output")
    parser.add_argument("--bin", action="store_true", help="read from or write to byte stream or string")
    parser.add_argument("--inf", default="xml", help="input format, one of: xml, yml, evt (default: xml)")
    parser.add_argument("--outf", default="xml", help="output format, one of: xml, yml, evt, py (default: xml)")
    parser.add_argument("--pretty", action="store_true", help="pretty parse/unparse")
    parser.add_argument("--filter", default="obj", help="intermefdiate filter, one of: obj, evt (default: obj)")
    parser.add_argument("input", nargs="?", help="input file or stdin")
    parser.add_argument("output", nargs="?", help="output file or stdout")
    args = parser.parse_args()
    if args.inf not in ["xml", "yml", "py"]:
        parser.exit(2, "%s: error: argument to --inf is invalid\n" % parser.prog)
    if args.outf not in ["xml", "yml", "py"]:
        parser.exit(2, "%s: error: argument to --outf is invalid\n" % parser.prog)
    if args.filter not in ["obj", "evt"]:
        parser.exit(2, "%s: error: argument to --filter is invalid\n" % parser.prog)
    if args.filter == "evt" and args.inf not in ["xml", "py"]:
        parser.exit(2, "%s: error: input format incompatible with filter\n" % parser.prog)
    if args.filter == "evt" and args.outf not in ["xml", "py"]:
        parser.exit(2, "%s: error: output format incompatible with filter\n" % parser.prog)
    if args.input == None or args.input == "-":
        args.input = sys.stdin
    else:
        args.input = open(args.input, "rb") if args.bin else open(args.input, "r")
    if args.output == None or args.output == "-":
        args.output = sys.stdout
    else:
        args.output = open(args.output, "wb") if args.bin else open(args.output, "w")

    in_process = None
    if args.in_process:
        in_process = lambda x: x.replace(args.in_process[0], args.in_process[1])
    out_process = None
    if args.out_process:
        out_process = lambda x: x.replace(args.out_process[0], args.out_process[1])

    if args.inf == "py":
        if args.filter == "obj":
            root = eval(args.input.read())
        else:
            events = eval(args.input.read())
    elif args.inf == "xml":
        if args.string:
            args.input = args.input.read()
            if not args.bin and isinstance(args.input, bytes):
                args.input = args.input.decode(args.in_encoding)
        if args.filter == "evt":
            if not args.test:
                events = xml_to_events(args.input, process_content=in_process, encoding=args.in_encoding)
            else:
                try:
                    events = xml_to_events(args.input, process_content=in_process, encoding=args.in_encoding)
                except Exception as e:
                    events = events_from_obj({"exception": str(e).encode("utf-8").decode("utf-8")})
        else:
            if not args.test:
                root = xml_to_obj(
                    args.input,
                    strip_space=args.pretty,
                    fold_dict=args.pretty,
                    process_content=in_process,
                    encoding=args.in_encoding,
                )
            else:
                try:
                    root = xml_to_obj(
                        args.input,
                        strip_space=args.pretty,
                        fold_dict=args.pretty,
                        process_content=in_process,
                        encoding=args.in_encoding,
                    )
                except Exception as e:
                    root = {"exception": str(e).encode("utf-8").decode("utf-8")}
    elif args.inf == "yml":
        if args.string:
            args.input = args.input.read()
            if not args.bin and isinstance(args.input, bytes):
                args.input = args.input.decode(args.in_encoding)
        root = obj_from_yaml(args.input, encoding=args.in_encoding, process_string=in_process)
    if args.outf == "xml":
        if args.filter == "obj":
            if args.string:
                string = xml_from_obj(
                    root, outf=None, pretty=args.pretty, process_content=out_process, encoding=args.out_encoding
                )
                if sys.version_info[0] >= 3 and args.bin == False:
                    string = string.decode(args.out_encoding)
                args.output.write(string)
            else:
                xml_from_obj(
                    root, args.output, pretty=args.pretty, process_content=out_process, encoding=args.out_encoding
                )
        else:
            xml_from_events(events, args.output, process_content=out_process, encoding=args.out_encoding)
    elif args.outf == "yml":
        if args.filter == "obj":
            if args.string:
                string = obj_to_yaml(root, outf=None, encoding=args.out_encoding, process_string=out_process)
                if sys.version_info[0] >= 3 and args.bin == False:
                    string = string.decode(args.out_encoding)
                args.output.write(string)
            else:
                obj_to_yaml(root, args.output, encoding=args.out_encoding, process_string=out_process)
    elif args.outf == "py":
        if args.filter == "obj":
            args.output.write(str(root))
        else:
            args.output.write(str(events))
