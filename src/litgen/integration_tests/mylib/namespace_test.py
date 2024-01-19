from __future__ import annotations
import lg_mylib


def test_namespace():
    assert "details" not in dir(lg_mylib)

    assert "local_function" not in dir(lg_mylib)

    assert "inner" in dir(lg_mylib)
    assert lg_mylib.inner.foo_inner() == 45
    assert lg_mylib.inner.foo_inner2() == 46
