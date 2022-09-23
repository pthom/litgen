import numpy as np
import lg_mylib


def test_c_buffers():
    #
    # Non templated call
    #
    x = np.array((1, 2, 3, 4, 5), np.uint8)
    lg_mylib.add_inside_buffer(x, 5)
    assert (x == np.array((6, 7, 8, 9, 10), np.uint8)).all()
    #
    # templated call
    #
    # With default float type
    x = np.array((1.0, 2.0, 3.0))
    lg_mylib.mul_inside_buffer(x, 3.0)
    assert (x == np.array((3.0, 6.0, 9.0))).all()
    # With default int type
    x = np.array((1, 2, 3))
    lg_mylib.mul_inside_buffer(x, 3)
    assert (x == np.array((3, 6, 9))).all()
    # With range of types
    data_types = [np.float32, np.uint8, np.uint32, np.int64]  # np.float128 is not supported by all versions of numpy
    for data_type in data_types:
        x = np.array((1, 2, 3), data_type)
        lg_mylib.mul_inside_buffer(x, 3)
        assert (x == np.array((3, 6, 9), data_type)).all()
    # With unsupported type (float16 is not supported by C++)
    got_exception = False
    data_type = np.float16
    x = np.array((1, 2, 3), data_type)
    try:
        lg_mylib.mul_inside_buffer(x, 3)
    except RuntimeError:
        got_exception = True
    assert got_exception
