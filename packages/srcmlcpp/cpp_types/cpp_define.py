from __future__ import annotations
from dataclasses import dataclass

from srcmlcpp.cpp_types.base import (
    CppElementAndComment,
    CppElementComments,
    CppElementsVisitorEvent,
    CppElementsVisitorFunction,
)
from srcmlcpp.srcml_wrapper import SrcmlWrapper


__all__ = ["CppDefine"]


@dataclass
class CppDefine(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html##define

    srcmlcpp xml "#define MY_ANSWER(x) (x+ 1)"

        <?xml version="1.0" ?>
        <unit xmlns="http://www.srcML.org/srcML/src" xmlns:ns1="http://www.srcML.org/srcML/cpp" revision="1.0.0" language="C++">
           <ns1:define>
              #
              <ns1:directive>define</ns1:directive>

              <ns1:macro>
                 <name>MY_ANSWER</name>
                 <parameter_list>
                    (
                    <parameter>
                       <type>
                          <name>x</name>
                       </type>
                    </parameter>
                    )
                 </parameter_list>
              </ns1:macro>
              <ns1:value>(x+ 1)</ns1:value>
           </ns1:define>
        </unit>
    """

    macro_name: str
    macro_parameters_str: str
    macro_value: str

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    def name(self) -> str:
        return self.macro_name

    def str_code(self) -> str:
        assert hasattr(self, "macro_name")
        r = f"#define {self.macro_name}"
        if hasattr(self, "macro_parameters_str"):
            r += self.macro_parameters_str
        if hasattr(self, "macro_value"):
            r += " " + self.macro_value
        return r

    def __str__(self) -> str:
        return self.str_code()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)


class CppConditionMacro(CppElementAndComment):
    """Stores preprocessor macros like #if, #ifdef, #ifndef, #endif, #else, #elif"""

    macro_code: str  # a verbatim copy of the C(++) code for this macro (including spaces and LF)

    def __init__(self, element: SrcmlWrapper, cpp_element_comments: CppElementComments) -> None:
        super().__init__(element, cpp_element_comments)

    def str_code(self) -> str:
        return self.macro_code.rstrip()

    def __str__(self):
        return self.str_code()

    def visit_cpp_breadth_first(self, cpp_visitor_function: CppElementsVisitorFunction, depth: int = 0) -> None:
        cpp_visitor_function(self, CppElementsVisitorEvent.OnElement, depth)
