from __future__ import annotations
import lg_mylib


def test_pointer_accept_none():
    point = lg_mylib.PointAcceptNone()
    point.value = 3
    assert lg_mylib.accept_none_value_or(point, -1) == 3
    assert lg_mylib.accept_none_value_or(None, -1) == -1
    assert point.accept_none_add(point) == 6
    assert point.accept_none_add(None) == 3


def test_return_pointer_optional():
    assert lg_mylib.maybe_none_point(True) is not None
    assert lg_mylib.maybe_none_point(False) is None
    assert lg_mylib.accept_none_value_or(lg_mylib.maybe_none_point(False), -1) == -1
