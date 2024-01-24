# pyright: reportAttributeAccessIssue=false
from __future__ import annotations
import lg_mylib
import pytest


def test_class_doc():
    assert lg_mylib.MyClass.__doc__ is not None
    assert "This is the class doc" in lg_mylib.MyClass.__doc__


def test_class_construction():
    my_struct = lg_mylib.MyClass(factor=42, message="World")
    assert my_struct.factor == 42
    assert my_struct.message == "World"


def test_simple_class_members():
    my_struct = lg_mylib.MyClass()

    my_struct.factor = 42
    assert my_struct.factor == 42


def test_stl_container_members():
    my_struct = lg_mylib.MyClass()
    assert len(my_struct.numbers) == 0

    my_struct.numbers.append(1)
    assert len(my_struct.numbers) == 0

    my_struct.append_number_from_cpp(42)
    assert my_struct.numbers == [42]


def test_fixed_size_numeric_array_members():
    foo = lg_mylib.MyClass()

    assert (foo.values == [0, 1]).all()
    foo.values[0] = 42
    assert (foo.values == [42, 1]).all()

    assert (foo.flags == [False, True, False]).all()
    foo.flags[0] = True
    assert (foo.flags == [True, True, False]).all()

    assert not hasattr(foo, "points")


def test_class_simple_methods():
    my_struct = lg_mylib.MyClass()
    my_struct.set_message("aaa")
    assert my_struct.message == "aaa"


def test_class_static_methods():
    assert lg_mylib.MyClass.static_message() == "Hi!"


def test_class_static_member():
    assert lg_mylib.MyClass.const_static_value == 101
    assert lg_mylib.MyClass.static_value == 102

    o = lg_mylib.MyClass()
    with pytest.raises(AttributeError):
        o.const_static_value = 103

    o.static_value = 104
    assert lg_mylib.MyClass.static_value == 104


def test_struct_not_registered():
    assert "Struct_Detail" not in dir(lg_mylib)


def test_unpublished_method():
    assert "unpublished_method" not in dir(lg_mylib.MyClass)


def test_singleton():
    i = lg_mylib.MySingletonClass.instance()
    assert i.value == 0
    i.value = 3
    i2 = lg_mylib.MySingletonClass.instance()
    assert i2.value == 3


def test_final_class():
    with pytest.raises(TypeError):

        class MyFinalClassDeriv(lg_mylib.MyFinalClass):
            pass


def test_dynamic_class():
    dynamic_instance = lg_mylib.MyStructDynamic()
    assert dynamic_instance.cpp_member == 1
    dynamic_instance.new_attrib = "Aye"
    assert dynamic_instance.new_attrib == "Aye"

    non_dyn_instance = lg_mylib.MyClass()
    with pytest.raises(AttributeError):
        non_dyn_instance.new_attrib = "Aye"


def test_nested_enum():
    c = lg_mylib.MyStructWithNestedEnum()
    assert c.handle_choice() == 0
    assert c.handle_choice(lg_mylib.MyStructWithNestedEnum.Choice.a) == 0
