# pyright: reportArgumentType=false
from __future__ import annotations
import lg_mylib
import pytest


def test_add_templated():
    assert lg_mylib.add_templated("Hello, ", "you") == "Hello, you"
    assert lg_mylib.add_templated(1, 2) == 3
    assert lg_mylib.add_templated(1.5, 2.5) == 4.0


def test_sum_vector_and_c_array():
    assert lg_mylib.sum_vector_and_c_array_int([1, 2, 3], [4, 5]) == 15
    assert lg_mylib.sum_vector_and_c_array_string(["a"], ["b", "c"]) == "abc"

    with pytest.raises(TypeError):
        # This will throw, since the second arg should have two elements
        _ = lg_mylib.sum_vector_and_c_array_int([1, 2, 3], [4])


def test_sum_vector_and_c_array_method():
    foo = lg_mylib.FooTemplateFunctionTest()
    assert foo.sum_vector_and_c_array_int([1, 2, 3], [4, 5]) == 15
    assert foo.sum_vector_and_c_array_string(["a"], ["b", "c"]) == "abc"

    with pytest.raises(TypeError):
        # This will throw, since the second arg should have two elements
        _ = foo.sum_vector_and_c_array_int([1, 2, 3], [4])  # type: ignore
