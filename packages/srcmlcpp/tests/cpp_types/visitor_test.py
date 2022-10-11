from codemanip import code_utils

import srcmlcpp
from srcmlcpp.cpp_types import *
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def test_visitor():
    options = SrcmlcppOptions()
    code = "int a = 1;"
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)

    visit_recap = ""

    def my_visitor(element: CppElement, event: CppElementsVisitorEvent, depth: int) -> None:
        nonlocal visit_recap

        if event == CppElementsVisitorEvent.OnElement:
            type_name = type(element).__name__

            code = element.str_code_verbatim().strip()
            code_first_line = code.split("\n")[0].strip()

            info = f"{type_name} ({code_first_line})"
            visit_recap += "  " * depth + info + "\n"

    cpp_unit.visit_cpp_breadth_first(my_visitor)
    # logging.warning("\n" + visit_recap)
    code_utils.assert_are_codes_equal(
        visit_recap,
        """
        CppUnit (int a = 1;)
          CppDeclStatement (int a = 1;)
            CppDecl (int a = 1;)
              CppType (int)
          """,
    )
