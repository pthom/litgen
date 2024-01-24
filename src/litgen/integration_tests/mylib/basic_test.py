# pyright: reportArgumentType=false
from __future__ import annotations
import lg_mylib
import pytest


def test_functions():
    assert lg_mylib.my_add(3, 4) == 7

    assert lg_mylib.my_mul(3, 4) == 12
    assert lg_mylib.my_sub(3, 4) == -1


def test_not_published():
    assert "my_div" not in dir(lg_mylib)


def test_doc():
    assert lg_mylib.my_sub.__doc__ is not None
    assert "Subtracts two numbers" in lg_mylib.my_sub.__doc__

    assert lg_mylib.my_add.__doc__ is not None
    assert "Adds two numbers" in lg_mylib.my_add.__doc__
    assert (
        "Title that should be published as a top comment" not in lg_mylib.my_add.__doc__
    )

    assert lg_mylib.my_mul.__doc__ == "my_mul(a: int, b: int) -> int\n"


def test_generic_function():
    r = lg_mylib.my_generic_function(1, 2, 3, a=4, b=5, c=6)
    assert r == 9  # == args.size() + 2 * kwargs.size()


def test_vectorizable_functions():
    assert lg_mylib.math_functions.vectorizable_sum(1, 2) == 3

    import numpy as np

    x = np.array([[1, 3], [5, 7]])
    y = np.array([[2, 4], [6, 8]])
    z = lg_mylib.math_functions.vectorizable_sum(x, y)
    expected = np.array([[3.0, 7.0], [11.0, 15.0]])
    assert (z == expected).all()


def test_ignored_namespace():
    assert "detail" not in dir(lg_mylib)
    with pytest.raises(AttributeError):
        _ = lg_mylib.detail.foo()  # type: ignore
