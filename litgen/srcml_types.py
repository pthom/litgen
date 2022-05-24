import logging
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

    def __init__(self):
        self.start: CodePosition = None
        self.end: CodePosition = None
        self.srcml_element = None


@_dataclass
class CppBlockChild(CppElement):
    """Any token that can be embedded in a CppBlock (expr_stmt, function_decl, decl_stmt, ...)"""
    def __init__(self):
        super().__init__()

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
        super().__init__()
        self.block_children: List[CppBlockChild] = []

    def _str_block(self, is_enum_block: bool = False):
        result = ""
        previous_child = None
        for child in self.block_children:
            child_str = str(child)
            if len(child_str) == 0:
                continue

            add_new_line = True
            if previous_child == None:
                add_new_line = False
            if previous_child is not None and isinstance(child, CppComment):
                if child.start.line == previous_child.end.line:
                    add_new_line = False
                    result += " "

            if add_new_line:
                result += "\n"

            if is_enum_block and isinstance(child, CppDecl):
                result += str(child)+ ","
            else:
                result += str(child)

            previous_child = child

        return result

    def _str_block_enum(self):
        return self._str_block(is_enum_block=True)

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

    Note about composed types:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """
    names: List[str]

    # specifiers: could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    specifiers: List[str]

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"], ["..."]
    modifiers: List[str]

    # template arguments types i.e ["int"] for vector<int>
    # (this will not be filled: see note about composed types)
    argument_list: List[str]

    def __init__(self):
        super().__init__()
        self.names = []
        self.specifiers = []
        self.modifiers = []
        self.argument_list = []

    @staticmethod
    def authorized_modifiers():
        return ["*", "&", "&&", "..."]

    def __str__(self):
        from litgen.internal.srcml import SrcMlException

        nb_const = self.specifiers.count("const")

        if nb_const > 2:
            raise ValueError("I cannot handle more than two `const` occurences in a type!")

        specifiers = self.specifiers
        if nb_const == 2:
            # remove the last const and handle it later
            specifier_r: List[str] = list(reversed(specifiers))
            specifier_r.remove("const")
            specifiers = list(reversed(specifier_r))

        specifiers_str = code_utils.join_remove_empty(" ", specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        # if len(self.names) == 0 and "..." not in self.modifiers:
        #     # this can happen with cast operators
        #     # Example:
        #     #   struct Foo
        #     #   {
        #     #     inline operator int();
        #     #   };
        #     # We raise an exception, and this operator will be ignored
        #     # raise SrcMlException(self.srcml_element, None, "CppType: len(self.names) = 0")

        name = " ".join(self.names)

        name_and_arg = name
        if len(self.argument_list) > 0:
            args_str = ", ".join(self.argument_list)
            name_and_arg += "<" + args_str + ">"

        strs = [specifiers_str, name_and_arg, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)

        if nb_const == 2:
            r += " const"

        return r


@_dataclass
class CppDecl(CppElement):
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

    def __init__(self):
        super().__init__()

    def __str__(self):
        cpp_type = str(self.cpp_type) if self.cpp_type is not None else ""
        type_and_name = code_utils.join_remove_empty(" ", [cpp_type, self.name])
        r = type_and_name
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



@_dataclass
class CppDeclStatement(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """
    cpp_decls: List[CppDecl]  # A CppDeclStatement can initialize several variables

    def __init__(self):
        super().__init__()
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
    decl: CppDecl = None

    template_type: CppType = None  # This is only for template's CppParameterList
    template_name: str = ""

    def __init__(self):
        super().__init__()

    def __str__(self):
        if self.decl is not None:
            assert self.template_type is None
            return str(self.decl)
        else:
            if self.template_type is None:
                logging.warning("CppParameter.__str__() with no decl and no template_type")
            return str(self.template_type) + " " + self.template_name


@_dataclass
class CppParameterList(CppElement):
    """
    List of parameters of a function
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    parameters: List[CppParameter]
    def __init__(self):
        super().__init__()
        self.parameters = []

    def __str__(self):
        strs = list(map(lambda param: str(param), self.parameters))
        return  code_utils.join_remove_empty(", ", strs)


@_dataclass
class CppTemplate(CppElement):
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """
    parameter_list: CppParameterList = CppParameterList()

    def __init__(self):
        super().__init__()

    def __str__(self):
        params_str = str(self.parameter_list)
        result = f"template<{params_str}>"
        return result


@_dataclass
class CppFunctionDecl(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """
    specifiers: List[str] # "const" or ""
    type: CppType = None
    name: str = ""
    parameter_list: CppParameterList = None
    template: CppTemplate = None

    def __init__(self):
        super().__init__()
        self.specifiers: List[str] = []

    def _str_decl(self):
        r = ""
        if self.template is not None:
            r += str(self.template) + " "
        r += f"{self.type} {self.name}({self.parameter_list})"
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
    block: CppBlock = None

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
    specifiers: List[str]
    name: str = ""
    parameter_list: CppParameterList = None

    def __init__(self):
        super().__init__()
        self.specifiers: List[str] = []

    def _str_decl(self):
        r = f"{self.name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
        return r

    def __str__(self):
        r = self._str_decl() +  ";"
        return r


@_dataclass
class CppContructor(CppContructorDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor
    """
    block: CppBlock = None
    # member_init_list: Any = None   # Not handled by litgen

    def __init__(self):
        super().__init__()

    def __str__(self):
        r = self._str_decl() + " : OMITTED_MEMBER_INIT_LIST { OMITTED_CONSTRUCTOR_CODE; }"
        return r


@_dataclass
class CppSuper(CppElement):
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """
    specifier: str # public, private or protected inheritance
    name: str      # name of the super class

    def __init__(self):
        super().__init__()

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
        super().__init__()
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
    super_list: CppSuperList = None
    block: CppBlock = None
    template: CppTemplate = None    # for template classes or structs

    def __init__(self):
        super().__init__()

    def _str_struct_or_class(self, is_class: bool):
        r = ""
        if self.template is not None:
            r += str(self.template) + "\n"
        if is_class:
            r += f"class {self.name}"
        else:
            r += f"struct {self.name}"
        if self.super_list is not None and len(str(self.super_list)) > 0:
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
    def __init__(self):
        super().__init__()

    def __str__(self):
        return self._str_struct_or_class(True)


@_dataclass
class CppComment(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    """
    text: str = "" # Warning, the text contains "//" or "/* ... */"

    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.text


@_dataclass
class CppNamespace(CppBlockChild):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """
    name: str = ""
    block: CppBlock = None

    def __init__(self):
        super().__init__()

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
    block: CppBlock = None

    def __init__(self):
        super().__init__()

    def __str__(self):
        if type == "class":
            r = f"enum class {self.name}\n"
        else:
            r = f"enum {self.name}\n"
        r += "{\n"

        block_code = self.block._str_block_enum()
        r += code_utils.indent_code(block_code, 4)

        r += "\n};\n"
        return r


@_dataclass
class CppExprStmt(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    def __init__(self):
        super().__init__()


@_dataclass
class CppExprStmt(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    def __init__(self):
        super().__init__()


@_dataclass
class CppReturn(CppBlockChild):
    """Not handled, we do not need it in the context of litgen"""
    def __init__(self):
        super().__init__()
