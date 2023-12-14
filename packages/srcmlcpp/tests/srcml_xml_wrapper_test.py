from __future__ import annotations
from codemanip import code_utils
from codemanip.code_position import CodePosition

import srcmlcpp.srcmlcpp_main
from srcmlcpp import SrcmlWrapper
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions
from srcmlcpp.srcmlcpp_main import code_to_srcml_wrapper


def test_srcml_cpp():
    options = SrcmlcppOptions()
    code = code_utils.unindent_code(
        """
    // doc about a
    int a = 5;
    int add(int a, int b) { return a + b; }
    double b = 3;

    struct Foo
    {
        double value;
    };
    """,
        flag_strip_empty_lines=True,
    )

    # test code_verbatim
    code_wrapper = code_to_srcml_wrapper(options, code, "main.h")
    assert code_wrapper.str_code_verbatim() == code

    # Test child_with_tag
    function_wrapper = code_wrapper.wrapped_children_with_tag("function")
    assert len(list(function_wrapper)) == 1

    # Test children with tag
    decl_stmt_wrappers = code_wrapper.wrapped_children_with_tag("decl_stmt")
    assert len(decl_stmt_wrappers) == 2

    first_decl_stmt = decl_stmt_wrappers[0]
    assert first_decl_stmt.str_code_verbatim() == "int a = 5;"

    # Test start/end position
    assert first_decl_stmt.start() == CodePosition(2, 1)
    assert first_decl_stmt.end() == CodePosition(2, 10)

    # test xml string
    first_decl_xml_str = first_decl_stmt.str_xml(beautify=False)
    # logging.warning("\n" + first_decl_xml_str)
    first_decl_xml_str = first_decl_stmt.str_xml(beautify=True)
    # logging.warning("\n" + first_decl_xml_str)
    expected_xml_str = """
        <?xml version="1.0" ?>
        <decl_stmt xmlns="http://www.srcML.org/srcML/src" xmlns:pos="http://www.srcML.org/srcML/position" pos:start="2:1" pos:end="2:10">
           <decl pos:start="2:1" pos:end="2:9">
              <type pos:start="2:1" pos:end="2:3">
                 <name pos:start="2:1" pos:end="2:3">int</name>
              </type>

              <name pos:start="2:5" pos:end="2:5">a</name>

              <init pos:start="2:7" pos:end="2:9">
                 =
                 <expr pos:start="2:9" pos:end="2:9">
                    <literal type="number" pos:start="2:9" pos:end="2:9">5</literal>
                 </expr>
              </init>
           </decl>
           ;
        </decl_stmt>
    """

    def remove_xmlns_lines(s: str) -> str:
        lines = s.split("\n")

        def not_is_xmlns(line: str) -> bool:
            return "xmlns" not in line

        lines = list(filter(not_is_xmlns, lines))
        r = "\n".join(lines)
        return r

    first_decl_xml_str = first_decl_xml_str.replace("ns0:", "")
    code_utils.assert_are_codes_equal(remove_xmlns_lines(first_decl_xml_str), remove_xmlns_lines(expected_xml_str))


def test_visitor():
    options = SrcmlcppOptions()
    code = code_utils.unindent_code(
        """
    namespace ns
    {
        int a;
        struct Foo;
    }
    """,
        flag_strip_empty_lines=True,
    )
    xml_tree = srcmlcpp.code_to_srcml_wrapper(options, code)

    visit_recap = ""

    def my_visitor(element: SrcmlWrapper, depth: int) -> None:
        nonlocal visit_recap
        if element.has_xml_name():
            name = element.extract_name_from_xml()
        else:
            name = "None"
        spacing = "  " * depth
        info = f"{spacing}tag: {element.tag()} name:{name}"
        visit_recap += info + "\n"

    xml_tree.visit_xml_breadth_first(my_visitor)
    # logging.warning("\n" + visit_recap)
    code_utils.assert_are_codes_equal(
        visit_recap,
        """
tag: unit name:None
  tag: namespace name:ns
    tag: name name:None
    tag: block name:None
      tag: decl_stmt name:None
        tag: decl name:a
          tag: type name:int
            tag: name name:None
          tag: name name:None
      tag: struct_decl name:Foo
        tag: name name:None
        """,
    )
