import os
import sys

from codemanip import code_utils

from srcmlcpp.internal import srcml_caller, srcml_utils


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def assert_code_unmodified_by_srcml(code: str) -> None:
    """
    We transform the code to xml (srcML), and assert that it can safely be translated back to the same code
    """
    root = srcml_caller.code_to_srcml(code)
    code2 = srcml_caller.srcml_to_code(root)
    assert code2 == code


def test_srcml_xml():
    code = "int a = 1"
    element = srcml_caller.code_to_srcml(code, False)
    xml_str = srcml_utils.srcml_to_str(element)
    expected_xml_str = """
        <?xml version="1.0" ?>
        <unit xmlns="http://www.srcML.org/srcML/src" revision="1.0.0" language="C++">
           <decl>
              <type>
                 <name>int</name>
              </type>

              <name>a</name>

              <init>
                 =
                 <expr>
                    <literal type="number">1</literal>
                 </expr>
              </init>
           </decl>
        </unit>
    """

    code_utils.assert_are_codes_equal(xml_str, expected_xml_str)


def test_srcml_does_not_modify_code():
    assert_code_unmodified_by_srcml("int a    =    1;   // With utf8 and special chars: 😜 Héloïse € ")
    assert_code_unmodified_by_srcml("void foo(int x, int y=5){};")
    assert_code_unmodified_by_srcml(
        """
    #include <nonexistingfile.h>
    #define TRUC
    // A super nice function
    template<typename T> constexpr T add(const T& a, T b) { return a + b;}

    /* A dummy comment */
                            ;;TRUC;;TRUC; TRUC TRUC   ;;;; // and some gratuitous elements
    // A lambda
    auto fnSub = [](int a, int b) { return b - a;};
    """
    )
