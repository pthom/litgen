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
enum Foo
{
    a, // This is a

    // And this is b and c's comment
    b,
    c = MY_VALUE,


    Foo_count, // And this is count

    d = a | b + c // And a computed value
};
    """
    enum = srcml_main.code_first_enum(options.srcml_options, code)
    adapted_enum = AdaptedEnum(enum, options)
    decls = adapted_enum.get_decls()

    assert len(decls) == 4  # Foo_count should have been removed
    assert decls[0].cpp_element().initial_value_code == "0"
    assert decls[0].cpp_element().cpp_element_comments.comment_end_of_line == " This is a"
    assert decls[1].cpp_element().initial_value_code == "1"
    assert decls[2].cpp_element().initial_value_code == "256"
    assert decls[3].cpp_element().initial_value_code == "a | b + c"


test_adapted_enum()
