from __future__ import annotations
import lg_mylib


def test_operators():
    a = lg_mylib.IntWrapper(6)
    b = lg_mylib.IntWrapper(4)

    # test arithmetic operators
    assert (a + b).value == 10
    assert (a - b).value == 2

    # Test unary minus
    assert (-a).value == -6

    # Test two versions of += (with IntWrapper and int)
    a += lg_mylib.IntWrapper(2)
    assert a.value == 8
    a += 2
    assert a.value == 10

    # Test two versions of the call operator (with IntWrapper and int)
    assert a(lg_mylib.IntWrapper(4)) == 42
    assert a(4) == 43


def test_spaceship_operator():
    a = lg_mylib.IntWrapperSpaceship(0)
    b = lg_mylib.IntWrapperSpaceship(1)

    assert a < b
    assert a < 1

    assert a <= b
    assert a <= 1

    assert a == 0
    assert a == lg_mylib.IntWrapperSpaceship(0)

    assert b >= a
    assert b >= 0

    assert b > a
    assert b > 0
