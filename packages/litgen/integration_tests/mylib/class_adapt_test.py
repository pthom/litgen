from __future__ import annotations
import lg_mylib


def test_adapt_constructor():
    c = lg_mylib.Color4([1, 2, 3, 4])
    assert c.rgba[0] == 1
    assert c.rgba[1] == 2
    assert c.rgba[2] == 3
    assert c.rgba[3] == 4


def test_modify_array_member_via_numpy_array():
    c = lg_mylib.Color4([0, 0, 0, 0])
    c.rgba[0] = 1
    c.rgba[1] = 2
    c.rgba[2] = 3
    c.rgba[3] = 4
    assert c.rgba[0] == 1
    assert c.rgba[1] == 2
    assert c.rgba[2] == 3
    assert c.rgba[3] == 4
