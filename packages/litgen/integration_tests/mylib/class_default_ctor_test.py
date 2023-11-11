from __future__ import annotations
import lg_mylib


def test_class_no_default_ctor():
    c = lg_mylib.a.ClassNoDefaultCtor(a=42, b=False, c=43)
    assert c.a == 42
    assert c.c == 43
    assert not c.b
    assert c.s == "Allo"
    assert c.foo == lg_mylib.a.Foo.foo1
