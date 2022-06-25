import logging

from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcml_xml_wrapper import SrcmlXmlWrapper
from codemanip import code_utils
from codemanip.code_position import CodePosition


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
    code_wrapper = SrcmlXmlWrapper.from_code(options, code)
    assert code_wrapper.code_verbatim() == code

    # Test child_with_tag
    function_wrapper = code_wrapper.child_with_tag("function")
    assert function_wrapper is not None

    # Test children with tag
    decl_stmt_wrappers = code_wrapper.children_with_tag("decl_stmt")
    assert len(decl_stmt_wrappers) == 2

    first_decl_stmt = decl_stmt_wrappers[0]
    assert first_decl_stmt.code_verbatim() == "int a = 5;\n"

    # Test start/end position
    assert first_decl_stmt.start_position() == CodePosition(2, 1)
    assert first_decl_stmt.end_position() == CodePosition(2, 10)

    # test xml string
    first_decl_xml_str = first_decl_stmt.as_xml_str(beautify=False)
    # logging.warning("\n" + first_decl_xml_str)
    expected_xml_str = '<ns0:decl_stmt xmlns:ns0="http://www.srcML.org/srcML/src" xmlns:ns1="http://www.srcML.org/srcML/position" ns1:start="2:1" ns1:end="2:10"><ns0:decl ns1:start="2:1" ns1:end="2:9"><ns0:type ns1:start="2:1" ns1:end="2:3"><ns0:name ns1:start="2:1" ns1:end="2:3">int</ns0:name></ns0:type> <ns0:name ns1:start="2:5" ns1:end="2:5">a</ns0:name> <ns0:init ns1:start="2:7" ns1:end="2:9">= <ns0:expr ns1:start="2:9" ns1:end="2:9"><ns0:literal type="number" ns1:start="2:9" ns1:end="2:9">5</ns0:literal></ns0:expr></ns0:init></ns0:decl>;</ns0:decl_stmt>\n'
    assert first_decl_xml_str == expected_xml_str
    first_decl_xml_str = first_decl_stmt.as_xml_str(beautify=True)
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
    code_wrapper = SrcmlXmlWrapper.from_code(options, code)
    yaml_str = code_wrapper.as_yaml()
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
