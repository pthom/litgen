import lg_mylib


def test_my_virtual_class():
    m = lg_mylib.Root.Inner.MyVirtualClass()
    assert m.foo() == 42
    assert m.foo2() == 44
    assert m.foo3() == 46
