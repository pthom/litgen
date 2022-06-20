import pytest  # type:ignore

import srcmlcpp
from srcmlcpp import srcml_main
from srcmlcpp.srcml_types import *

import litgen
from litgen.internal.adapted_types_wip.adapted_types import *


def test_adapted_enum():
    options = litgen.LitgenOptions()
    options.srcml_options.named_number_macros = {"MY_VALUE": 256}

    code = """
// Doc about Foo
// On several lines
enum Foo
{
    Foo_a, // This is a

    // And this is b and c's comment
    Foo_b,
    Foo_c = MY_VALUE,

    Foo_d = Foo_a | Foo_b + Foo_c, // And a computed value

    Foo_e = 4,

    Foo_count, // And this is count
};
    """
    enum = srcml_main.code_first_enum(options.srcml_options, code)
    adapted_enum = AdaptedEnum(enum, options)
    decls = adapted_enum.get_decls()

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
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(Enum):
            """ Doc about Foo
             On several lines
            """
            foo_a = 0                                                 # This is a

            #  And this is b and c's comment
            foo_b = 1
            foo_c = 256

            foo_d = Literal[Foo.a] | Literal[Foo.b] + Literal[Foo.c]  # And a computed value

            foo_e = 4
    ''',
    )

    # Test generated stub code (with python_reproduce_cpp_layout=False)
    options.python_reproduce_cpp_layout = False
    stub_code = str(adapted_enum)
    code_utils.assert_are_codes_equal(
        stub_code,
        '''
        class Foo(Enum):
            """ Doc about Foo
             On several lines
            """
            #  This is a
            foo_a = 0
            #  And this is b and c's comment
            foo_b = 1
            foo_c = 256
            #  And a computed value
            foo_d = Literal[Foo.a] | Literal[Foo.b] + Literal[Foo.c]
            foo_e = 4
        ''',
    )


test_adapted_enum()
