from __future__ import annotations
import lg_mylib


def test_c_string_list():
    strings = ["Hello", "Wonderful", "World"]
    a = lg_mylib.BoxedInt()
    b = lg_mylib.BoxedInt()
    total_size = lg_mylib.c_string_list_total_size(strings, a, b)
    assert total_size == len("Hello") + len("Wonderful") + len("World")
    assert a.value == total_size
    assert b.value == total_size + 1
