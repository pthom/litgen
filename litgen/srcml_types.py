from dataclasses import dataclass as _dataclass
from typing import Optional, List, Tuple
import litgen.internal.code_utils as code_utils

import xml.etree.ElementTree as ET

'''

Note about CppBlock an CppBlockContent: the distinction betwen the two is not very clear. 

- For functions and anonymous blocks, the code is inside <block><block_content>
- For namespaces, the code is inside <block> (without <block_content>)
- For classes and structs the code is inside <block><private or public>

They are a versatile container for decl_stmt, function, function_decl, enul, expr_stmt, etc.
Here is the list of classes related to blocks handling:

    class CppBlockChild(CppElement):
        """Any token that can be embedded in a CppBlock (expr_stmt, function_decl, decl_stmt, ...)"""
        pass

    class CppBlock(CppElement, CppBlockChild):
        """Any block inside a function, an anonymous block, a namespace, or in a public/protected/private zone        
            - For functions and anonymous blocks, the code is inside <block><block_content>
            - For namespaces, the code is inside <block> (without <block_content>)
            - For classes and structs the code is inside <block><private or public>
            
            https://www.srcml.org/doc/cpp_srcML.html#block
        """ 
        block_children: List[CppBlockChild]

    class CppBlockContent(CppBlock):
        """A kind of block used by function and anonymous blocks, where the code is inside <block><block_content>
           This can be viewed as a sub-block with a different name
        """

    class CppPublicProtectedPrivate(CppBlock, CppBlockChild):
        """A kind of block defined by a public/protected/private zone in a struct or in a class
        See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
        Note: this is not a direct adaptation. Here we merge the different access types, and we derive from CppBlockContent
        """
        access_type: str # "public", "private", or "protected"


Below, an output of the xml tree for function, anonymous blocks, namespaces and classes:

Type: function / code = void foo() {}
****************************************
<?xml version="1.0" ?>
<ns0:function
    xmlns:ns0="http://www.srcML.org/srcML/src">
    <ns0:type>
        <ns0:name>void</ns0:name>
    </ns0:type>
    <ns0:name>foo</ns0:name>
    <ns0:parameter_list>()</ns0:parameter_list>
    <ns0:block>
{

        <ns0:block_content/>
}

    </ns0:block>
</ns0:function>


Type: block / code = {}
****************************************
<?xml version="1.0" ?>
<ns0:block xmlns:ns0="http://www.srcML.org/srcML/src">
{
    <ns0:block_content/>
}
</ns0:block>


Type: namespace / code = namespace Foo {}
****************************************
<?xml version="1.0" ?>
<ns0:namespace xmlns:ns0="http://www.srcML.org/srcML/src">
    namespace 
    <ns0:name>Foo</ns0:name>
    <ns0:block>{}</ns0:block>
</ns0:namespace>


Type: class / code = class Foo {}
****************************************
<?xml version="1.0" ?>
<ns0:class xmlns:ns0="http://www.srcML.org/srcML/src">
    class 
    <ns0:name>Foo</ns0:name>    
    <ns0:block>
        {
        <ns0:private type="default"/>
        }
    </ns0:block>
    <ns0:decl/>
</ns0:class>
'''


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
    """Base class for all the Cpp Elements below. It contains their start/end position in the original code
    """
    start: CodePosition
    end: CodePosition


@_dataclass
class CppBlockChild(CppElement):
    """Any token that can be embedded in a CppBlock (expr_stmt, function_decl, decl_stmt, ...)"""
    pass


@_dataclass
class CppBlock(CppElement): # it is also a CppBlockChild
    """Any block inside a function, an anonymous block, a namespace, or in a public/protected/private zone
        - For functions and anonymous blocks, the code is inside <block><block_content>
        - For namespaces, the code is inside <block> (without <block_content>)
        - For classes and structs the code is inside <block><private or public>

        https://www.srcml.org/doc/cpp_srcML.html#block

        Can contain these types of child tags:
            child_tag='decl_stmt'
            child_tag='function_decl'
            child_tag='comment'
            child_tag='function'
            child_tag='struct'
            child_tag='namespace'
            child_tag='enum' (optionally type="class")
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
        r += self._str_block()
        return r


@_dataclass
class CppType(CppElement):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type
    """
    name: str
    specifiers: List[str]    # could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    modifiers: List[str]     # could be ["*"], ["&&"], ["&"], ["*", "*"]
    argument_list: List[str] # template arguments i.e ["int"] for vector<int>

    def __init__(self):
        self.name = ""
        self.specifiers = []
        self.modifiers = []
        self.argument_list = []

    def __str__(self):
        specifiers_str = code_utils.join_remove_empty(" ", self.specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        name_and_arg = self.name
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
        strs = list(map(str, self.cpp_decls))
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

    def __str__(self):
        r = f"{self.type} {self.name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
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
        r = CppFunctionDecl.__str__(self) + " { OMITTED_BLOCK; }"
        # r += "\n{\n"
        # r += code_utils.indent_code( str(self.block), 4)
        # r += "\n}\n"
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
