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


def test_templated_sum_buffers():
    # templated_sum_buffers takes two templated buffers: both numpy arrays must share the same dtype,
    # since the C++ function is templated on a single type T.

    # Matched dtype (int) -> works
    x = np.array((1, 2, 3), np.int32)
    y = np.array((10, 20, 30), np.int32)
    assert lg_mylib.templated_sum_buffers(x, y) == 66.0

    # Matched dtype (float) -> works
    xf = np.array((1.0, 2.0, 3.0), np.float64)
    yf = np.array((0.5, 0.5, 0.5), np.float64)
    assert lg_mylib.templated_sum_buffers(xf, yf) == 7.5

    # Mismatched dtype -> raises an explicit, actionable error (cf. issue imgui_bundle#467).
    # Without the dtype guard, buffer_1's bytes would be silently reinterpreted as buffer_2's type.
    with pytest.raises(RuntimeError) as exc_info:
        lg_mylib.templated_sum_buffers(
            np.array((1, 2, 3), np.int64),
            np.array((1.0, 2.0, 3.0), np.float64),
        )
    message = str(exc_info.value)
    assert "share the same dtype" in message
    assert "astype(" in message
    # Full message test (may discard later, if too brittle)
    assert (
        message
        == 'templated_sum_buffers: all numeric arrays must share the same dtype, but "buffer_1" has dtype int64 while "buffer_2" has dtype float64. Convert them to a common dtype, e.g. buffer_1 = buffer_1.astype(buffer_2.dtype).'
    )
