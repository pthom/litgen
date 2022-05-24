from dataclasses import dataclass as _dataclass
from typing import Optional, List, Tuple
import litgen.internal.code_utils as code_utils

import xml.etree.ElementTree as ET


@_dataclass
class CodePosition:
    """Position of an element in the code"""
    line: int = 0
    column: int = 0

    @staticmethod
    def from_string(s: str): # -> CodePosition:
        """Parses a string like '3:5' which means line 3, column 5 """
        items = s.split(":")
        assert len(items) == 2
        r = CodePosition()
        r.line = int(items[0])
        r.column = int(items[1])
        return r

    def __str__(self):
        return f"{self.line}:{self.column}"


class CppElement:
    """Base class for all the Cpp Elements below.
    - It contains their start/end position in the original code
    - It also contains the original Xml Element from which it was constructed
    """
    start: CodePosition
    end: CodePosition
    srcml_element: ET.Element


@_dataclass
class CppBlockChild(CppElement):
    """Any token that can be embedded in a CppBlock (expr_stmt, function_decl, decl_stmt, ...)"""
    pass


@_dataclass
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
    block_children: List[CppBlockChild]

    def __init__(self):
        self.block_children: List[CppBlockChild] = []

    def _str_block(self):
        strs = map(str, self.block_children)
        result = code_utils.join_remove_empty("\n", strs)
        return result

    def __str__(self):
        return self._str_block()


@_dataclass
class CppUnit(CppBlock):
    """A kind of block representing a full file.
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        r = self._str_block() + "\n"
        return r


@_dataclass
class CppBlockContent(CppBlock):
    """A kind of block used by function and anonymous blocks, where the code is inside <block><block_content>
       This can be viewed as a sub-block with a different name
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        r = ""
        r += "// <CppBlockContent>\n"
        r += self._str_block() + "\n"
        r += "// </CppBlockContent>\n"
        return r


@_dataclass
class CppPublicProtectedPrivate(CppBlock): # Also a CppBlockChild
    """A kind of block defined by a public/protected/private zone in a struct or in a class

    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types, and we derive from CppBlockContent
    """
    access_type: str # "public", "private", or "protected"

    def __init__(self, access_type):
        super().__init__()
        self.access_type = access_type

    def __str__(self):
        r = f"{self.access_type}:\n"
        r += code_utils.indent_code(self._str_block(), 4)
        return r


@_dataclass
class CppType(CppElement):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """
    names: List[str]

    # specifiers: could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    specifiers: List[str]

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"]
    modifiers: List[str]

    # template arguments types i.e ["int"] for vector<int>
    argument_list: List[str]

    def __init__(self):
        self.names = []
        self.specifiers = []
        self.modifiers = []
        self.argument_list = []

    @staticmethod
    def authorized_modifiers():
        return ["*", "&", "&&"]

    def __str__(self):
        specifiers_str = code_utils.join_remove_empty(" ", self.specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        assert len(self.names) > 0
        name = " ".join(self.names)

        name_and_arg = name
        if len(self.argument_list) > 0:
            args_str = ", ".join(self.argument_list)
            name_and_arg += "<" + args_str + ">"

        strs = [specifiers_str, name_and_arg, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)
        return r


@_dataclass
class CppDecl(CppElement):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration

    Note: init_cpp is inside an <init><expr> node in srcML. Here we retransform it to C++ code for simplicity
        For example:
            int a = 5;
            <decl_stmt><decl><type><name>int</name></type> <name>a</name> <init>= <expr><literal type="number">5</literal></expr></init></decl>;</decl_stmt>
    """
    cpp_type: CppType = CppType()
    name: str = ""
    init: str = ""  # initial or default value

    def __str__(self):
        r = f"{self.cpp_type} {self.name}"
        if len(self.init) > 0:
            r += " = " + self.init
        return r


@_dataclass
class CppDeclStatement(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    cpp_decls: List[CppDecl]  # A CppDeclStatement can initialize several variables

    def __init__(self):
        self.cpp_decls = []

    def __str__(self):
        strs = list(map(lambda cpp_decl: str(cpp_decl) + ";", self.cpp_decls))
        r = code_utils.join_remove_empty("\n", strs)
        return r


@_dataclass
class CppParameter(CppElement):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    decl: CppDecl = CppDecl()

    def __str__(self):
        return str(self.decl)


@_dataclass
class CppParameterList(CppElement):
    """
    List of parameters of a function
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    parameters: List[CppParameter]
    def __init__(self):
        self.parameters = []

    def __str__(self):
        strs = list(map(lambda param: str(param), self.parameters))
        return  code_utils.join_remove_empty(", ", strs)


@_dataclass
class CppFunctionDecl(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    specifiers: List[str] # "const" or ""
    type: CppType = CppType()
    name: str = ""
    parameter_list: CppParameterList = CppParameterList()

    def __init__(self):
        self.specifiers: List[str] = []

    def _str_decl(self):
        r = f"{self.type} {self.name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
        return r

    def __str__(self):
        r = self._str_decl() +  ";"
        return r


@_dataclass
class CppFunction(CppFunctionDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """
    block: CppBlock = CppBlock()

    def __init__(self):
        super().__init__()

    def __str__(self):
        r = self._str_decl() + " { OMITTED_FUNCTION_CODE; }"
        return r


@_dataclass
class CppContructorDecl(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """
    specifier: str = ""
    name: str = ""
    parameter_list: CppParameterList = CppParameterList()

    def __str__(self):
        r = f"{self.type} {self.name}({self.parameter_list})"
        return r


@_dataclass
class CppSuper(CppElement):
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    specifier: str # public, private or protected inheritance
    name: str      # name of the super class

    def __str__(self):
        if len(self.specifier) > 0:
            return f"{self.specifier} {self.name}"
        else:
            return self.name


@_dataclass
class CppSuperList(CppElement):
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    super_list: List[CppSuper]

    def __init__(self):
        self.super_list: List[CppSuper] = []

    def __str__(self):
        strs = map(str, self.super_list)
        return code_utils.join_remove_empty(", ", strs)


@_dataclass
class CppStruct(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    name: str = ""
    super_list: CppSuperList = CppSuperList()
    block: CppBlock = CppBlock()

    def _str_struct_or_class(self, is_class: bool):
        if is_class:
            r = f"class {self.name}"
        else:
            r = f"struct {self.name}"
        if len(str(self.super_list)) > 0:
            r += " : "
            r += str(self.super_list)

        r += "\n{\n"
        r +=  code_utils.indent_code(str(self.block), 4) + "\n"
        r += "};\n"

        return r

    def __str__(self):
        return self._str_struct_or_class(False)


@_dataclass
class CppClass(CppStruct):
    """
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """
    def __str__(self):
        return self._str_struct_or_class(True)


@_dataclass
class CppComment(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    """
    text: str = "" # Warning, the text contains "//" or "/* ... */"

    def __str__(self):
        return self.text


@_dataclass
class CppNamespace(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    name: str = ""
    block: CppBlock = CppBlock()

    def __str__(self):
        r = f"namespace {self.name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "\n}\n"
        return r


@_dataclass
class CppEnum(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """
    type: str = ""  # "class" or ""
    name: str = ""
    block: CppBlock = CppBlock()

    def __str__(self):
        if type == "class":
            r = f"enum class {self.name}\n"
        else:
            r = f"enum {self.name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "\n}\n"
        return r


@_dataclass
class CppExprStmt(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    pass


@_dataclass
class CppExprStmt(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    pass


@_dataclass
class CppReturn(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    pass
