from __future__ import annotations
import lg_mylib
import numpy as np
import pytest


def test_add_inside_buffer():
    x = np.array((1, 2, 3, 4, 5), np.uint8)
    lg_mylib.add_inside_buffer(x, 5)
    assert (x == np.array((6, 7, 8, 9, 10), np.uint8)).all()

    # Test that array of other types are rejected
    with pytest.raises(RuntimeError) as exc_info:
        x = np.array((1, 2, 3, 4, 5), np.uint16)
        lg_mylib.add_inside_buffer(x, 5)
    exception_message = str(exc_info.value)
    assert "Bad type!" in exception_message


def test_buffer_sum():
    x = np.array((1, 2, 3, 4, 5), np.uint8)
    result_sum = lg_mylib.buffer_sum(x)
    assert result_sum == 15


def test_add_inside_two_buffers():
    x = np.array((1, 2, 3), np.uint8)
    y = np.array((10, 11, 12), np.uint8)
    lg_mylib.add_inside_two_buffers(x, y, 5)
    assert (x == np.array((6, 7, 8), np.uint8)).all()
    assert (y == np.array((15, 16, 17), np.uint8)).all()


def test_templated_mul_inside_buffer():
    # With default float type
    x = np.array((1.0, 2.0, 3.0))
    lg_mylib.templated_mul_inside_buffer(x, 3.0)
    assert (x == np.array((3.0, 6.0, 9.0))).all()

    # With default int type
    x = np.array((1, 2, 3))
    lg_mylib.templated_mul_inside_buffer(x, 3)
    assert (x == np.array((3, 6, 9))).all()

    # With range of types
    data_types = [
        np.float32,
        np.uint8,
        np.uint32,
        np.int64,
    ]  # np.float128 is not supported by all versions of numpy
    for data_type in data_types:
        x = np.array((1, 2, 3), data_type)
        lg_mylib.templated_mul_inside_buffer(x, 3)
        assert (x == np.array((3, 6, 9), data_type)).all()

    # With unsupported type (float16 is not supported by C++)
    got_exception = False
    data_type = np.float16
    x = np.array((1, 2, 3), data_type)
    try:
        lg_mylib.templated_mul_inside_buffer(x, 3)
    except RuntimeError:
        got_exception = True
    assert got_exception
