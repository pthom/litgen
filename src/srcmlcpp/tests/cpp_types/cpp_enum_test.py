from __future__ import annotations
from typing import cast

from srcmlcpp.cpp_types import CppEnum, CppDecl
import srcmlcpp


def test_c_enum():
    options = srcmlcpp.SrcmlcppOptions()
    code = """
    enum Color {
        Color_Red = 0,
        Color_Green,

        // A standalone comment

        Color_Blue
    };
    """

    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    enum_color = cast(CppEnum, cpp_unit.all_elements_of_type(CppEnum)[0])
    assert not enum_color.is_enum_class()

    enum_decls = enum_color.get_enum_decls()
    assert enum_decls[0].initial_value_code == "0"
    assert enum_decls[1].initial_value_code == ""
    assert enum_decls[2].initial_value_code == ""

    enum_children = enum_color.get_children_with_filled_decl_values()
    assert len(enum_children) == 6  # 3 decl + 2 empty lines + 1 comment
    assert isinstance(enum_children[1], CppDecl)
    assert enum_children[1].initial_value_code == "1"


def test_enum_class():
    options = srcmlcpp.SrcmlcppOptions()
    code = """
    enum class Color {
        Color_Red = 0,
        Color_Green,
        Color_Blue
    };
    """

    cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
    enum_color = cast(CppEnum, cpp_unit.all_elements_of_type(CppEnum)[0])
    assert enum_color.is_enum_class()
