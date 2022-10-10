from codemanip import code_utils
from codemanip.code_position import CodePosition

import srcmlcpp.srcmlcpp_main
from srcmlcpp import SrcmlWrapper
from srcmlcpp.internal.srcmlcpp_exception_detailed import SrcmlcppExceptionDetailed
from srcmlcpp.srcmlcpp_exception import SrcmlcppException
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcmlcpp_main import code_to_srcml_xml_wrapper


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
    code_utils.assert_are_codes_equal(first_decl_xml_str, expected_xml_str)


def test_warnings():
    options = SrcmlOptions()
    options.flag_show_python_callstack = True
    code = "void foo(int a);"

    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code, filename="main.h")
    decl = cpp_unit.block_children[0]

    got_exception = False
    try:
        raise SrcmlcppExceptionDetailed(decl, "Artificial exception")
    except SrcmlcppException as e:
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

    def my_visitor(element: SrcmlWrapper, depth: int) -> None:
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
