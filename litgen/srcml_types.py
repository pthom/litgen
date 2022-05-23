from dataclasses import dataclass as _dataclass
from typing import Optional, List, Tuple
import litgen.internal.code_utils as code_utils


class SrcmlBase:
    pass


@_dataclass
class CppType(SrcmlBase):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type
    """
    name: str
    specifiers: List[str] # could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    modifiers: List[str]  # could be ["*"], ["&&"], ["&"], ["*", "*"]

    def __init__(self):
        self.name = ""
        self.specifiers = []
        self.modifiers = []

    def __str__(self):
        specifiers_str = code_utils.join_remove_empty(" ", self.specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)
        strs = [specifiers_str, self.name, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)
        return r


@_dataclass
class CppDecl(SrcmlBase):
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
class CppDeclStatement(SrcmlBase):
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
class CppParameter(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    decl: CppDecl = CppDecl()

    def __str__(self):
        return str(self.decl)


@_dataclass
class CppParameterList(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    parameters: List[CppParameter]
    def __init__(self):
        self.parameters = []

    def __str__(self):
        strs = list(map(lambda param: str(param), self.parameters))
        return  code_utils.join_remove_empty(", ", strs)


@_dataclass
class CppFunctionDecl(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    type: CppType = CppType()
    name: str = ""
    parameter_list: CppParameterList = CppParameterList()

    def __str__(self):
        r = f"{self.type} {self.name}({self.parameter_list})"
        return r


@_dataclass
class CppSuper(SrcmlBase):
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
class CppSuperList(SrcmlBase):
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
class CppBlockContent(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#block_content
    """
    pass


@_dataclass
class CppPublicProtectedPrivate(SrcmlBase):
    """
    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types
    """
    access_type: str # "public", "private", or "protected"

    def __init__(self, access_type):
        self.access_type = access_type


@_dataclass
class CppBlock(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#block
    """
    public_protected_private: List[CppPublicProtectedPrivate]
    block_content: CppBlockContent = CppBlockContent()

    def __init__(self):
        self.public_protected_private: List[CppPublicProtectedPrivate] = []


@_dataclass
class CppStruct(SrcmlBase):
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    name: str = ""
    super_list: CppSuperList = CppSuperList()
    block: CppBlock = CppBlock()

    def __str__(self):
        r = f"struct {self.name}"
        if len(str(self.super_list)) > 0:
            r += " : "
            r += str(self.super_list)

        r += "\n{\n"
        r +=  code_utils.indent_code(str(self.block), 4) + "\n"
        r += "};\n"

        return r
