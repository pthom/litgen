from dataclasses import dataclass as _dataclass
from typing import Optional, List, Tuple


@_dataclass
class CppType:
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


@_dataclass
class CppDecl:
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


@_dataclass
class CppDeclStatement:
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    cpp_decls: List[CppDecl]  # A CppDeclStatement can initialize several variables

    def __init__(self):
        self.cpp_decls = []


@_dataclass
class CppParameter:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    decl: CppDecl = CppDecl()


@_dataclass
class CppParameterList:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    parameters: List[CppParameter]
    def __init__(self):
        self.parameters = []


@_dataclass
class CppFunctionDecl:
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    type: CppType = CppType()
    name_cpp: str = ""
    parameter_list: CppParameterList = CppParameterList()


