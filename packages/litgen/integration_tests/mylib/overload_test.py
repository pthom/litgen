from __future__ import annotations
import lg_mylib


def test_overload():
    assert lg_mylib.add_overload(3, 4) == 7
    assert lg_mylib.add_overload(3, 4, 3) == 10

    foo = lg_mylib.FooOverload()
    assert foo.add_overload(3, 4) == 7
    assert foo.add_overload(3, 4, 3) == 10
