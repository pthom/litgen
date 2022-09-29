from codemanip.code_position import CodePosition

import srcmlcpp.srcmlcpp_main
from srcmlcpp import SrcMlException, SrcMlExceptionDetailed
from srcmlcpp.srcmlcpp_main import code_to_srcml_xml_wrapper
from srcmlcpp.srcml_types import *


def test_srcml_cpp():
    options = SrcmlOptions()
    code = code_utils.unindent_code(
        """
    // doc about a
    int a = 5;
    int add(int a, int b) { return a + b; }
    double b = 3;
    // _SRCML_EMPTY_LINE_
    struct Foo
    {
        double value;
    };
    """,
        flag_strip_empty_lines=True,
    )

    # test code_verbatim
    code_wrapper = code_to_srcml_xml_wrapper(options, code, "main.h")
    assert code_wrapper.str_code_verbatim() == code

    # Test child_with_tag
    function_wrapper = code_wrapper.wrapped_children_with_tag("function")
    assert len(list(function_wrapper)) == 1

    # Test children with tag
    decl_stmt_wrappers = code_wrapper.wrapped_children_with_tag("decl_stmt")
    assert len(decl_stmt_wrappers) == 2

    first_decl_stmt = decl_stmt_wrappers[0]
    assert first_decl_stmt.str_code_verbatim() == "int a = 5;\n"

    # Test start/end position
    assert first_decl_stmt.start() == CodePosition(2, 1)
    assert first_decl_stmt.end() == CodePosition(2, 10)

    # test xml string
    first_decl_xml_str = first_decl_stmt.str_xml(beautify=False)
    # logging.warning("\n" + first_decl_xml_str)
    expected_xml_str = '<ns0:decl_stmt xmlns:ns0="http://www.srcML.org/srcML/src" xmlns:ns1="http://www.srcML.org/srcML/position" ns1:start="2:1" ns1:end="2:10"><ns0:decl ns1:start="2:1" ns1:end="2:9"><ns0:type ns1:start="2:1" ns1:end="2:3"><ns0:name ns1:start="2:1" ns1:end="2:3">int</ns0:name></ns0:type> <ns0:name ns1:start="2:5" ns1:end="2:5">a</ns0:name> <ns0:init ns1:start="2:7" ns1:end="2:9">= <ns0:expr ns1:start="2:9" ns1:end="2:9"><ns0:literal type="number" ns1:start="2:9" ns1:end="2:9">5</ns0:literal></ns0:expr></ns0:init></ns0:decl>;</ns0:decl_stmt>\n'
    assert first_decl_xml_str == expected_xml_str
    first_decl_xml_str = first_decl_stmt.str_xml(beautify=True)
    # logging.warning("\n" + first_decl_xml_str)
    expected_xml_str = """
        <?xml version="1.0" ?>
        <ns0:decl_stmt xmlns:ns0="http://www.srcML.org/srcML/src" xmlns:ns1="http://www.srcML.org/srcML/position" ns1:start="2:1" ns1:end="2:10">
           <ns0:decl ns1:start="2:1" ns1:end="2:9">
              <ns0:type ns1:start="2:1" ns1:end="2:3">
                 <ns0:name ns1:start="2:1" ns1:end="2:3">int</ns0:name>
              </ns0:type>

              <ns0:name ns1:start="2:5" ns1:end="2:5">a</ns0:name>

              <ns0:init ns1:start="2:7" ns1:end="2:9">
                 =
                 <ns0:expr ns1:start="2:9" ns1:end="2:9">
                    <ns0:literal type="number" ns1:start="2:9" ns1:end="2:9">5</ns0:literal>
                 </ns0:expr>
              </ns0:init>
           </ns0:decl>
           ;
        </ns0:decl_stmt>
    """
    code_utils.assert_are_codes_equal(first_decl_xml_str, expected_xml_str)


def test_yaml():
    options = SrcmlOptions()
    code = "int a = 5;"
    code_wrapper = code_to_srcml_xml_wrapper(options, code)
    yaml_str = code_wrapper.str_yaml()
    expected_yaml = code_utils.unindent_code(
        """
        ns0:unit:
        - '@filename': /var/folders/hj/vlpl655s0gz58f0tfgghv0g40000gn/T/tmp42146zwk.h
        - '@language': C++
        - '@ns1:tabs': '8'
        - '@revision': 1.0.0
        - '@xmlns:ns0': http://www.srcML.org/srcML/src
        - '@xmlns:ns1': http://www.srcML.org/srcML/position
        - ns0:decl_stmt:
          - '@ns1:end': '1:10'
          - '@ns1:start': '1:1'
          - ns0:decl:
            - '@ns1:end': '1:9'
            - '@ns1:start': '1:1'
            - ns0:type:
              - '@ns1:end': '1:3'
              - '@ns1:start': '1:1'
              - ns0:name:
                - '@ns1:end': '1:3'
                - '@ns1:start': '1:1'
                - int
            - ' '
            - ns0:name:
              - '@ns1:end': '1:5'
              - '@ns1:start': '1:5'
              - a
            - ' '
            - ns0:init:
              - '@ns1:end': '1:9'
              - '@ns1:start': '1:7'
              - '= '
              - ns0:expr:
                - '@ns1:end': '1:9'
                - '@ns1:start': '1:9'
                - ns0:literal:
                  - '@ns1:end': '1:9'
                  - '@ns1:start': '1:9'
                  - '@type': number
                  - '5'
          - ;
    """,
        flag_strip_empty_lines=True,
    )
    # logging.warning("\n" + yaml_str)

    # strip second line, that contains a dummy filename
    def strip_second_line(code: str) -> str:
        lines = code.split("\n")
        del lines[1]
        r = "\n".join(lines)
        return r

    code_utils.assert_are_codes_equal(strip_second_line(yaml_str), strip_second_line(expected_yaml))


def test_warnings():
    options = SrcmlOptions()
    options.flag_show_python_callstack = True
    code = "void foo(int a);"

    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code, filename="main.h")
    decl = cpp_unit.block_children[0]

    got_exception = False
    try:
        raise SrcMlExceptionDetailed(decl, "Artificial exception")
    except SrcMlException as e:
        got_exception = True
        msg = str(e)
        for part in [
            "test_warnings",
            "function_decl",
            "main.h:1:1",
            "void foo",
            "Artificial exception",
        ]:
            assert part in msg
    assert got_exception


def test_warnings_2():
    options = srcmlcpp.SrcmlOptions()
    code = code_utils.unindent_code(
        """
        struct __Foo
        {
            int a = 1;
        };
    """,
        flag_strip_empty_lines=True,
    )
    cpp_struct = srcmlcpp.srcmlcpp_main.code_first_struct(options, code)

    msg = cpp_struct._warning_message_str("names starting with __ are reserved")
    code_utils.assert_are_codes_equal(
        msg,
        """
        Warning: names starting with __ are reserved
        While parsing a "struct", corresponding to this C++ code:
        Position:1:1
            struct __Foo
            ^
            {
                int a = 1;
            };
    """,
    )


def test_visitor():
    options = SrcmlOptions()
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
    xml_tree = srcmlcpp.code_to_srcml_xml_wrapper(options, code)

    visit_recap = ""

    def my_visitor(element: SrcmlXmlWrapper, depth: int) -> None:
        nonlocal visit_recap
        if element.has_name():
            name = element.name_code()
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
