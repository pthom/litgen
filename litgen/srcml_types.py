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
    name_cpp: str
    specifiers: List[str] # could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    modifiers: List[str]  # could be ["*"], ["&&"], ["&"], ["*", "*"]

    def __init__(self):
        self.name_cpp = ""
        self.specifiers = []
        self.modifiers = []

    def __str__(self):
        specifiers_str = code_utils.join_remove_empty(" ", self.specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)
        strs = [specifiers_str, self.name_cpp, modifiers_str]
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
    name_cpp: str = ""
    init_cpp: str = ""

    def __str__(self):
        r = f"{self.cpp_type} {self.name_cpp}"
        if len(self.init_cpp) > 0:
            r += " = " + self.init_cpp
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
    name_cpp: str = ""
    parameter_list: CppParameterList = CppParameterList()

    def __str__(self):
        r = f"{self.type} {self.name_cpp}({self.parameter_list})"
        return r
