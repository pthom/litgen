from srcmlcpp.srcml_types import *

from litgen.internal.adapt_function import AdaptedFunction


class AdaptedElement:
    cpp_element: CppElementAndComment

    def __init__(self, cpp_element: CppElementAndComment):
        self.cpp_element = cpp_element


class AdaptedEmptyLine(AdaptedElement):
    def __init__(self, cpp_empty_line: CppEmptyLine):
        super().__init__(cpp_empty_line)


class AdaptedDecl(AdaptedElement):
    def __init__(self, decl: CppDecl):
        super().__init__(decl)


class AdaptedComment(AdaptedElement):
    def __init(self, cpp_comment: CppComment):
        super().__init__(cpp_comment)


class AdaptedConstructor(AdaptedElement):
    def __init__(self, ctor: CppConstructorDecl):
        super().__init__(ctor)


class AdaptedClass(AdaptedElement):
    def __init__(self, class_: CppStruct):
        super().__init__(class_)


class AdaptedEnum(AdaptedElement):
    cpp_enum: CppEnum


class AdaptedCppUnit(AdaptedElement):
    pass
