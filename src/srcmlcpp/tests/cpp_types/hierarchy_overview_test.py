from __future__ import annotations
from codemanip import code_utils

import srcmlcpp
from srcmlcpp.srcmlcpp_options import SrcmlcppOptions


def test_hierarchy_overview():
    code = """
    namespace Blah
    {
        struct Foo
        {
            enum A {
                a = 0;
            };
            void dummy();
        };
    }
    """
    options = SrcmlcppOptions()
    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    overview = cpp_unit.hierarchy_overview()
    # logging.warning("\n" + overview)
    code_utils.assert_are_codes_equal(
        overview,
        """
        CppUnit
          CppEmptyLine
          CppNamespace name=Blah
            CppBlock scope=Blah
              CppStruct name=Foo scope=Blah
                CppBlock scope=Blah::Foo
                  CppPublicProtectedPrivate scope=Blah::Foo
                    CppEnum name=A scope=Blah::Foo
                      CppBlock scope=Blah::Foo::A
                        CppDecl name=a scope=Blah::Foo
                        CppUnprocessed scope=Blah::Foo::A
                    CppFunctionDecl name=dummy scope=Blah::Foo
                      CppType name=void scope=Blah::Foo
                      CppParameterList scope=Blah::Foo
          CppEmptyLine
    """,
    )
