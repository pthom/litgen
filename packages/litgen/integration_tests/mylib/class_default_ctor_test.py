import lg_mylib


def test_class_no_default_ctor():
    c = lg_mylib.A.ClassNoDefaultCtor(a=42, b=False, c=43)
    assert c.a == 42
    assert c.c == 43
    assert not c.b
    assert c.s == "Allo"
    assert c.foo == lg_mylib.A.Foo.foo1
