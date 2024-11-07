from __future__ import annotations
from codemanip import code_utils

from srcmlcpp import srcmlcpp_main

import litgen
from litgen.internal import LitgenContext
from litgen.internal.adapted_types import AdaptedEnum


def test_adapted_enum():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.named_number_macros = {"MY_VALUE": 256}
    lg_context = LitgenContext(options)

    code = """
// Doc about Foo
// On several lines
enum Foo
{
    Foo_a, // This is a

    // And this is b and c's comment
    Foo_b,
    Foo_c = MY_VALUE,              // c has a special comment

    Foo_d = Foo_a | Foo_b + Foo_c, // And a computed value

    Foo_e = 4,

    Foo_count, // And this is count
};
    """
    enum = srcmlcpp_main.code_first_enum(options.srcmlcpp_options, code)
    adapted_enum = AdaptedEnum(lg_context, enum)
    decls = adapted_enum.adapted_enum_decls

    # Test parsing and adapt: count should be removed, members should be renamed, comment should be processed
    assert len(decls) == 5  # Foo_count should have been removed (becua
    assert decls[0].cpp_element().initial_value_code == "0"
    assert decls[0].cpp_element().cpp_element_comments.comment_end_of_line == " This is a"
    assert decls[1].cpp_element().initial_value_code == "1"
    assert decls[2].cpp_element().initial_value_code == "256"
    assert decls[3].cpp_element().initial_value_code == "Foo_a | Foo_b + Foo_c"

    # Test generated stub code (with python_reproduce_cpp_layout=True)
    options.python_reproduce_cpp_layout = True
    stub_code = str(adapted_enum)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(enum.Enum):
            """ Doc about Foo
             On several lines
            """
            a = enum.auto() # (= 0)  # This is a

            # And this is b and c's comment
            b = enum.auto() # (= 1)
            c = enum.auto() # (= 256)  # c has a special comment

            d = enum.auto() # (= Foo.a | Foo.b + Foo.c)  # And a computed value

            e = enum.auto() # (= 4)
    ''',
    )

    # Test generated stub code (with python_reproduce_cpp_layout=False)
    options.python_reproduce_cpp_layout = False
    stub_code = str(adapted_enum)
    # logging.warning("\n>>>" + stub_code + "<<<")
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(enum.Enum):
            """ Doc about Foo
             On several lines
            """

            # This is a
            a = enum.auto() # (= 0)

            # And this is b and c's comment

            b = enum.auto() # (= 1)
            # c has a special comment
            c = enum.auto() # (= 256)
            # And a computed value
            d = enum.auto() # (= Foo.a | Foo.b + Foo.c)
            e = enum.auto() # (= 4)
        ''',
    )

    # Test generated pydef code
    options.original_location_flag_show = True
    pydef_code = adapted_enum.str_pydef()
    # logging.warning("\n>>>" + pydef_code + "<<<")
    code_utils.assert_are_codes_equal(
        pydef_code,
        """
        auto pyEnumFoo =
            py::enum_<Foo>(m, "Foo", py::arithmetic(), " Doc about Foo\\n On several lines")    // Line:4
                .value("a", Foo_a, "This is a")
                .value("b", Foo_b, "")
                .value("c", Foo_c, "c has a special comment")
                .value("d", Foo_d, "And a computed value")
                .value("e", Foo_e, "");
    """,
    )


def test_enum_class():
    cpp_code = """
        enum class Foo
        {
            A,
            B,
            C = MY_VALUE,
            D = A | B + C,
            E = 4,
            F
        };
    """

    import litgen

    options = litgen.LitgenOptions()
    options.srcmlcpp_options.named_number_macros = {"MY_VALUE": 256}
    generated_code = litgen.generate_code(options, cpp_code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        class Foo(enum.Enum):
            a = enum.auto() # (= 0)
            b = enum.auto() # (= 1)
            c = enum.auto() # (= 256)
            d = enum.auto() # (= A | B + C)
            e = enum.auto() # (= 4)
            f = enum.auto() # (= 5)
        """,
    )
