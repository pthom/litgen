from __future__ import annotations
import lg_mylib


def test_foo_brace():
    f = lg_mylib.FooBrace()
    assert len(f.int_values) == 3
    assert "abc" in f.dict_string_int.keys()

    f2 = lg_mylib.FooBrace(int_values=[1])
    assert len(f2.int_values) == 1


def test_fn_brace():
    r = lg_mylib.fn_brace(ints=[4, 5, 6])
    assert r == 5

    r = lg_mylib.fn_brace(foo_brace=lg_mylib.FooBrace(int_values=[5]), ints=[5])
    assert r == 10
