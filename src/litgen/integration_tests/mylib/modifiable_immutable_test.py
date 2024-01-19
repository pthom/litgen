from __future__ import annotations
import lg_mylib


"""
See doc in modifiable_immutable_test.h
"""


def test_modifiable_immutable():
    a = lg_mylib.BoxedBool(True)
    assert a.value
    lg_mylib.toggle_bool_pointer(a)
    assert not a.value
    lg_mylib.toggle_bool_reference(a)
    assert a.value
    lg_mylib.toggle_bool_nullable(a)
    assert not a.value
    lg_mylib.toggle_bool_nullable(None)


def test_modify_string():
    s = lg_mylib.BoxedString("Say ")
    lg_mylib.modify_string(s)
    assert s.value == "Say hello"


def test_nullable_param():
    b = lg_mylib.BoxedBool(True)
    lg_mylib.toggle_bool_nullable(b)
    assert not b.value
    lg_mylib.toggle_bool_nullable()


#
# Test Part 2: in the functions below return type is modified:
# the following functions will return a tuple inside python :
#     (original_return_value, modified_paramer)
#
# This is caused by the following options during generation:
#
#     options.fn_params_output_modifiable_immutable_to_return__regex = r"^Slider"


def test_adapt_modifiable_immutable_to_return():
    r = lg_mylib.change_bool_int("Hello", 2)
    assert r == (True, 3)

    r = lg_mylib.change_void_int("Hello", 2)
    assert r == 3

    r = lg_mylib.change_bool_int2("Hello", 1, 2)
    assert r == (False, 2, 4)

    r = lg_mylib.change_void_int_default_null("Hello", None)
    assert r == (True, None)

    r = lg_mylib.change_void_int_default_null("Hello")
    assert r == (True, None)

    r = lg_mylib.change_void_int_default_null("Hello", 1)
    assert r == (True, 2)

    ints = [1, 2, 3]
    r = lg_mylib.change_void_int_array("Hello", ints)
    assert r == (True, [2, 4, 6])
