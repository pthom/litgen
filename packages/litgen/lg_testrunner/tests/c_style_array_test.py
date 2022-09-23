import lg_mylib


def test_c_array():
    #
    # Test const c arrays / non void function
    # MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}
    #
    a = [5, 6]
    r = lg_mylib.add_c_array2(a)
    assert r == 11

    got_exception = False
    try:
        lg_mylib.add_c_array2([1, 2, 3])
    except TypeError:
        got_exception = True
    assert got_exception

    #
    # Test const c arrays / void function
    # MY_API inline void log_c_array2(const int values[2]) { printf("%i, %i\n", values[0], values[1]); }
    #
    a = [5, 6]
    lg_mylib.log_c_array2(a)  # This should print "5, 6\n"

    #
    # Test non const c arrays with numeric type (which will be boxed)
    # MY_API inline void change_c_array(unsigned long values[2])
    # {
    #     values[0] = values[1] + values[0];
    # values[1] = values[0] * values[1];
    # }
    #
    a = lg_mylib.BoxedUnsignedLong(5)
    b = lg_mylib.BoxedUnsignedLong(6)
    lg_mylib.change_c_array2(a, b)
    assert a.value == 11
    assert b.value == 66

    # Test non const c arrays with struct type (which will *not* be boxed)
    #     MY_API inline void GetPoints(Point2 out[2]) { out[0] = {0, 1}; out[1] = {2, 3}; }
    pt1 = lg_mylib.Point2()
    pt2 = lg_mylib.Point2()
    lg_mylib.get_points(pt1, pt2)
    assert pt1.x == 0 and pt1.y == 1 and pt2.x == 2 and pt2.y == 3
