import lg_mylib


def test_overload():
    assert lg_mylib.add_overload(3, 4) == 7
    assert lg_mylib.add_overload(3, 4, 3) == 10
    fo = lg_mylib.FooOverload()
    assert fo.add_overload(3, 4) == 7
    assert fo.add_overload(3, 4, 3) == 10
