from __future__ import annotations
import lg_mylib


def test_extern():
    assert "extern_c_add" in dir(lg_mylib)
    assert lg_mylib.extern_c_add(1, 2) == 3


def test_void_param():
    assert lg_mylib.foo_void_param() == 42


def test_unnamed_param():
    assert lg_mylib.foo_unnamed_param(1, True, 3.2) == 42


def test_defines():
    assert "ANSWER_ZERO_COMMENTED" in dir(lg_mylib)
    assert lg_mylib.ANSWER_ZERO_COMMENTED == 0
    assert lg_mylib.ANSWER_ONE_COMMENTED == 1
    assert lg_mylib.HEXVALUE == 0x43242
    assert lg_mylib.OCTALVALUE == 0o43242
    assert lg_mylib.STRING == "Hello"
    assert lg_mylib.FLOAT == 3.14

    assert "ANSWER" not in dir(lg_mylib)
    assert "DEFINE_NO_VALUE" not in dir(lg_mylib)
    assert "BROKEN_FLOAT" not in dir(lg_mylib)
    assert "FUNCTION_CALL" not in dir(lg_mylib)
