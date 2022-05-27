from typing import List
import logging
import copy
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from litgen.internal.srcml import srcml_utils, srcml_caller
from litgen.internal import code_utils


@dataclass
class CodePosition:
    """Position of an element in the code"""
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"

    @staticmethod
    def from_string(s: str): # -> CodePosition:
        """Parses a string like '3:5' which means line 3, column 5 """
        items = s.split(":")
        assert len(items) == 2
        line = int(items[0])
        column = int(items[1])
        r = CodePosition(line, column)
        return r


@dataclass
class CppElementComments:
    comment_on_previous_lines: str = ""
    comment_end_of_line: str = ""

    def comment(self):
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line

    def as_dict(self):
        r = {
            "comment_top" : self.comment_on_previous_lines,
            "comment_eol" : self.comment_end_of_line
        }
        return r

    def top_comment_code(self):
        top_comments = map(lambda comment: "// "  + comment, self.comment_on_previous_lines.splitlines())
        top_comment = "\n".join(top_comments)
        if len(top_comment) > 0:
            top_comment += "\n"
        return top_comment

    def eol_comment_code(self):
        if len(self.comment_end_of_line) == 0:
            return ""
        else:
            return " // " + self.comment_end_of_line

    def full_comment(self):
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line

class CppElement:
    """Wrapper around a srcLML xml node.
    """
    srcml_element: ET.Element = None

    def __init__(self, srcml_element: ET.Element):
        assert isinstance(srcml_element, ET.Element)
        self.srcml_element = srcml_element

    def tag(self):
        return srcml_utils.clean_tag_or_attrib(self.srcml_element.tag)

    def text(self):
        """Text part of the xml element"""
        return srcml_utils.str_none_empty(self.srcml_element.text)

    def tail(self):
        """Tail part of the xml element"""
        return srcml_utils.str_none_empty(self.srcml_element.tail)

    def start(self) -> CodePosition:
        """Start position in the C++ code"""
        return srcml_utils.element_start_position(self.srcml_element)

    def end(self) -> CodePosition:
        """End position in the C++ code"""
        return srcml_utils.element_end_position(self.srcml_element)

    def has_name(self) -> bool:
        name_children = srcml_utils.children_with_tag(self.srcml_element, "name")
        return len(name_children) == 1

    def name(self) -> str:
        assert self.has_name()
        name_element = srcml_utils.child_with_tag(self.srcml_element, "name")
        if name_element.text is not None:
            return name_element.text
        else:
            return srcml_caller.srcml_to_code(name_element)

    def name_or_empty(self):
        if not self.has_name():
            return ""
        else:
            return self.name()

    def attribute_value(self, attr_name):
        if attr_name in self.srcml_element.attrib:
            return self.srcml_element.attrib[attr_name]
        else:
            return None

    def str_code_verbatim(self):
        """Return the exact C++ code from which this xml node was constructed by calling the executable srcml
        """
        return srcml_caller.srcml_to_code(self.srcml_element)

    def annotate_with_cpp_element_class(self, msg):
        class_name = str(self.__class__)
        items = class_name.split(".")
        class_name = items[-1][:-2]
        return f"[++{class_name}++]  {msg} [--{class_name}--]"

    def str_code(self):
        """Returns a C++ textual representation of the contained code element.
        By default, it returns an exact copy of the original code. Derived classes override this implementation
        with their own information and the generated code might differ a little from the original code.
        """
        return self.str_code_verbatim()

    def str_xml_readable(self):
        """Return the xml tree formatted in a yaml inspired format"""
        return srcml_utils.srcml_to_str_readable(self.srcml_element)

    def str_xml(self):
        """Returns the xml tree as an xml string representation"""
        return srcml_utils.srcml_to_str(self.srcml_element)

    def as_dict(self):
        as_dict = {
            "tag": self.tag(),
            "name": self.name_or_empty(),
            "text": self.text(),
            "start": str(self.start()),
            "end": str(self.end()),
        }
        return as_dict

    def __str__(self):
        return self.str_xml_readable()


@dataclass
class CppEmptyLine(CppElement):
    def __init__(self, element: ET.Element):
        super().__init__(element)

    def str_code(self):
        return ""

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False):
        return ""

    def __str__(self):
        return ""


@dataclass
class CppElementAndComment(CppElement):
    """A CppElement to which we add comments"""
    cpp_element_comments: CppElementComments

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        assert isinstance(element, ET.Element)
        super().__init__(element)
        self.cpp_element_comments = cpp_element_comments

    def as_dict(self):
        as_dict= code_utils.merge_dicts(super().as_dict(), self.cpp_element_comments.as_dict())
        return as_dict

    def str_commented(self, is_enum:bool = False, is_decl_stmt: bool = False):
        result = self.cpp_element_comments.top_comment_code()
        result +=  self.str_code()
        if is_enum:
            result += ","
        if is_decl_stmt:
            result += ";"
        result += self.cpp_element_comments.eol_comment_code()
        return result

    def __str__(self):
        return self.str_commented()


@dataclass
class CppBlockChild(CppElementAndComment):
    """Abstract parent class: any token that can be embedded in a CppBlock (expr_stmt, function_decl, decl_stmt, ...)"""
    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)


class CppUnprocessed(CppBlockChild):
    """Any Cpp Element that is not yet processed by srcmlcpp
    We keep its original source under the form of a string
    """
    code: str = ""

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        return f"<unprocessed_{self.tag()}/>"

    def __str__(self):
        return self.str_commented()


@dataclass
class CppBlock(CppElement): # it is also a CppBlockChild
    """The class CppBlock is a container that represents any set of code  detected by srcML. It has several derived classes.

        - For namespaces:
                Inside srcML we have this: <block>CODE</block>
                Inside python, the block is handled by `CppBlock`
        - For files (i.e "units"):
                Inside srcML we have this: <unit>CODE</unit>
                Inside python, the block is handled by `CppUnit` (which derives from `CppBlock`)
        - For functions and anonymous block:
                Inside srcML we have this:  <block><block_content>CODE</block_content></block>
                Inside python, the block is handled by `CppBlockContent` (which derives from `CppBlock`)
        - For classes and structs:
                Inside srcML we have this: <block><private or public>CODE</private or public></block>
                Inside python, the block is handled by `CppPublicProtectedPrivate` (which derives from `CppBlock`)

        https://www.srcml.org/doc/cpp_srcML.html#block
    """
    block_children: List[CppBlockChild] = None

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.block_children: List[CppBlockChild] = []

    def str_block(self, is_enum: bool = False):
        result = ""
        for i, child in enumerate(self.block_children):
            if i < len(self.block_children) - 1:
                child_str = child.str_commented(is_enum=is_enum)
            else:
                child_str = child.str_commented(is_enum=False)
            result += child_str
            if not child_str.endswith("\n"):
                result += "\n"
        return result

    def __str__(self):
        return self.str_block()


@dataclass
class CppUnit(CppBlock):
    """A kind of block representing a full file.
    """
    def __init__(self, element: ET.Element):
        super().__init__(element)

    def __str__(self):
        return self.str_block()


@dataclass
class CppBlockContent(CppBlock):
    """A kind of block used by function and anonymous blocks, where the code is inside <block><block_content>
       This can be viewed as a sub-block with a different name
    """
    def __init__(self, element: ET.Element):
        super().__init__(element)

    def __str__(self):
        return self.str_block()


@dataclass
class CppPublicProtectedPrivate(CppBlock): # Also a CppBlockChild
    """A kind of block defined by a public/protected/private zone in a struct or in a class

    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types, and we derive from CppBlockContent
    """
    access_type: str = "" # "public", "private", or "protected"
    type: str = ""        # "default" or "" ("default" means it was added automaticaly, as "public" for structs or "private" for classes)

    def __init__(self, element: ET.Element, access_type: str, type: str):
        super().__init__(element)
        assert type in [None, "", "default"]
        assert access_type in ["public", "protected", "private"]
        self.access_type = access_type
        self.type = type

    def str_ppp(self):
        r = ""

        r += f"{self.access_type}" + ":"
        if self.type == "default":
            r += "// <default_access_type/>"
        r += "\n"

        r += code_utils.indent_code(self.str_block(), 4)
        return r

    def str_code(self):
        return self.str_ppp()

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False):
        return self.str_code()

    def __str__(self):
        return self.str_ppp()


@dataclass
class CppType(CppElement):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note about composed types:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """
    names: List[str] = None

    # specifiers: could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    specifiers: List[str] = None

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"], ["..."]
    modifiers: List[str] = None

    # template arguments types i.e ["int"] for vector<int>
    # (this will not be filled: see note about composed types)
    # argument_list: List[str]

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.names: List[str] = []
        self.specifiers: List[str] = []
        self.modifiers: List[str] = []

    @staticmethod
    def authorized_modifiers():
        return ["*", "&", "&&", "..."]

    def str_code(self):
        from litgen.internal.srcml import SrcMlException

        nb_const = self.specifiers.count("const")

        if nb_const > 2:
            raise ValueError("I cannot handle more than two `const` occurrences in a type!")

        specifiers = self.specifiers
        if nb_const == 2:
            # remove the last const and handle it later
            specifier_r: List[str] = list(reversed(specifiers))
            specifier_r.remove("const")
            specifiers = list(reversed(specifier_r))

        specifiers_str = code_utils.join_remove_empty(" ", specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        name = " ".join(self.names)

        name_and_arg = name
        strs = [specifiers_str, name_and_arg, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)

        if nb_const == 2:
            r += " const"

        return r

    def __str__(self):
        return self.str_code()


@dataclass
class CppDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration

    Notes:
    * In certain cases, the name of a variable can be seen as a composition by srcML.
      For example:

        `int v[10];`

      Will yield the following tree for the name:

            <?xml version="1.0" ?>
            <ns0:name>
               <ns0:name>v</ns0:name>
               <ns0:index>
                  [
                  <ns0:expr>
                     <ns0:literal type="number">10</ns0:literal>
                  </ns0:expr>
                  ]
               </ns0:index>
            </ns0:name>

      In litgen, this name will be seen as "v[10]"

    * init represent the initial aka default value.
      With srcML, it is inside an <init><expr> node in srcML.
      Here we retransform it to C++ code for simplicity
        For example:
            int a = 5;

            leads to:
            <decl_stmt><decl><type><name>int</name></type> <name>a</name> <init>= <expr><literal type="number">5</literal></expr></init></decl>;</decl_stmt>

            Which is retranscribed as "5"
    """
    cpp_type: CppType = None
    name: str = ""
    init: str = ""  # initial or default value

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = srcml_utils.str_none_empty(self.cpp_type) + " " + str(self.name)
        if len(self.init) > 0:
            r += " = " + self.init
        return r

    def has_name_or_ellipsis(self):
        assert self.name is not None
        if len(self.name) > 0:
            return True
        elif "..." in self.cpp_type.modifiers:
            return True
        return False

    def __str__(self):
        r = self.str_commented()
        return r


@dataclass
class CppDeclStatement(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    cpp_decls: List[CppDecl] = None  # A CppDeclStatement can initialize several variables

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.cpp_decls: List[CppDecl] = []

    def str_code(self):
        str_decls = list(map(lambda cpp_decl: cpp_decl.str_commented(is_decl_stmt=True), self.cpp_decls))
        str_decl = code_utils.join_remove_empty("\n", str_decls)
        return str_decl

    def __str__(self):
        return self.str_commented()


@dataclass
class CppParameter(CppElement):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    decl: CppDecl = None

    template_type: CppType = None  # This is only for template's CppParameterList
    template_name: str = ""

    def __init__(self, element: CppElement):
        super().__init__(element)

    def str_code(self):
        if self.decl is not None:
            assert self.template_type is None
            return str(self.decl)
        else:
            if self.template_type is None:
                from litgen.internal.srcml import OPTIONS
                if not OPTIONS.flag_quiet:
                    logging.warning("CppParameter.__str__() with no decl and no template_type")
            return str(self.template_type) + " " + self.template_name

    def __str__(self):
        return self.str_code()


@dataclass
class CppParameterList(CppElement):
    """
    List of parameters of a function
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    parameters: List[CppParameter] = None

    def __init__(self, element: CppElement):
        super().__init__(element)
        self.parameters = []

    def str_code(self):
        strs = list(map(lambda param: str(param), self.parameters))
        return  code_utils.join_remove_empty(", ", strs)

    def __str__(self):
        return self.str_code()


@dataclass
class CppTemplate(CppElement):
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """
    parameter_list: CppParameterList = None

    def __init__(self, element: CppElement):
        super().__init__(element)
        self.parameter_list: List[CppParameterList] = []

    def str_code(self):
        params_str = f"template<{str(self.parameter_list)}>\n"
        return params_str

    def __str__(self):
        return self.str_code()


@dataclass
class CppFunctionDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    specifiers: List[str] = None # "const" or ""
    type: CppType = None
    name: str = ""
    parameter_list: CppParameterList = None
    template: CppTemplate = None
    is_auto_decl: bool = False # True if it is a decl of the form `auto square(double) -> double`

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.specifiers: List[str] = []

    def _str_signature(self):
        r = ""

        if self.template is not None:
            r += f"template<{str(self.template)}>"

        r += f"{self.type} {self.name}({self.parameter_list})"

        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " ".join(specifiers_strs)

        return r

    def str_code(self):
        r = self._str_signature() + ";"
        return r

    def __str__(self):
        return  self.str_commented()


@dataclass
class CppFunction(CppFunctionDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    block: CppUnprocessed = None

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = self._str_signature() + str(self.block)
        return r

    def __str__(self):
        r = ""
        if len(self.cpp_element_comments.top_comment_code()) > 0:
            r += self.cpp_element_comments.top_comment_code()
        r += self._str_signature() + self.cpp_element_comments.eol_comment_code()
        r += "\n" + str(self.block) + "\n"
        return r


@dataclass
class CppConstructorDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """
    specifiers: List[str]
    name: str = ""
    parameter_list: CppParameterList = None

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.specifiers: List[str] = []

    def _str_signature(self):
        r = f"{self.name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
        return r

    def str_code(self):
        return self._str_signature()

    def __str__(self):
        return self.str_commented()


@dataclass
class CppConstructor(CppConstructorDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor
    """
    block: CppUnprocessed = None
    member_init_list: CppUnprocessed = None

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = self._str_signature() + str(self.block)
        return r

    def __str__(self):
        r = ""
        if len(self.cpp_element_comments.top_comment_code()) > 0:
            r += self.cpp_element_comments.top_comment_code()
        r += self._str_signature() + self.cpp_element_comments.eol_comment_code()
        r += "\n" + str(self.block) + "\n"
        return r


@dataclass
class CppSuper(CppElement):
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    specifier: str = "" # public, private or protected inheritance
    name: str = "" # name of the super class

    def __init__(self, element: ET.Element):
        super().__init__(element)

    def str_code(self):
        if len(self.specifier) > 0:
            return f"{self.specifier} {self.name}"
        else:
            return self.name

    def __str__(self):
        return self.str_code()


@dataclass
class CppSuperList(CppElement):
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    super_list: List[CppSuper]

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.super_list: List[CppSuper] = []

    def str_code(self):
        strs = map(str, self.super_list)
        return " : " + code_utils.join_remove_empty(", ", strs)

    def __str__(self):
        return self.str_code()


@dataclass
class CppStruct(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    name: str = ""
    super_list: CppSuperList = None
    block: CppBlock = None
    template: CppTemplate = None    # for template classes or structs

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = ""
        if self.template is not None:
            r += str(self.template)

        if isinstance(self, CppClass):
            r += "class "
        elif isinstance(self, CppStruct):
            r += "struct "
        r += f"{self.name}"

        if self.super_list is not None and len(str(self.super_list)) > 0:
            r += str(self.super_list)

        r += "\n"

        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "};\n"

        return r

    def __str__(self):
        return self.str_commented()


@dataclass
class CppClass(CppStruct):
    """
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """
    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def __str__(self):
        return self.str_commented()


@dataclass
class CppComment(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    Warning, the text contains "//" or "/* ... */" and "\n"
    """
    comment: str

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        lines = self.comment.split("\n")       # split("\n") keeps empty lines (splitlines() does not!)
        lines = list(map(lambda s: "// " + s, lines))
        return "\n".join(lines)

    def __str__(self):
        return self.str_code()


@dataclass
class CppNamespace(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    name: str = ""
    block: CppBlock = None

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = f"namespace {self.name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "}"
        return r

    def __str__(self):
        return self.str_full()


@dataclass
class CppEnum(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """
    type: str = ""  # "class" or ""
    name: str = ""
    block: CppBlock = None

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = ""
        if self.type == "class":
            r += f"enum class {self.name}\n"
        else:
            r+= f"enum {self.name}\n"
        r += "{\n"
        block_code = self.block.str_block(is_enum=True)
        r += code_utils.indent_code(block_code, 4)
        r += "};\n"
        return r

    def __str__(self):
        return self.str_code()
