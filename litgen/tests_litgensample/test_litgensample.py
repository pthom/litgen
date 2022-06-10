import litgensample
import numpy as np


def test_c_array():
    #
    # Test const c arrays
    # MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}
    #
    a = (5, 6)
    r = litgensample.add_c_array2(a)
    assert r == 11

    got_exception = False
    try:
        litgensample.add_c_array2((1, 2, 3))
    except TypeError:
        got_exception = True
    assert got_exception

    #
    # Test non const c arrays
    # MY_API inline void change_c_array(unsigned long values[2])
    # {
    #     values[0] = values[1] + values[0];
    # values[1] = values[0] * values[1];
    # }
    #
    # a = [litgensample.BoxedUnsignedLong(5), litgensample.BoxedUnsignedLong(6)]
    # print(f"Before {a=}")
    # litgensample.change_c_array(a)
    # print(f"After {a=}")

    a = litgensample.BoxedUnsignedLong(5)
    b = litgensample.BoxedUnsignedLong(6)
    litgensample.change_c_array2(a, b)
    print(f"After {a=} {b=}")

test_c_array()
