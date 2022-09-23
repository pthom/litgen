import lg_mylib


def test_c_array_numeric_member_types():
    foo = lg_mylib.Foo()

    assert (foo.values == [0, 1]).all()
    foo.values[0] = 42
    assert (foo.values == [42, 1]).all()

    assert (foo.flags == [False, True, False]).all()
    foo.flags[0] = True
    assert (foo.flags == [True, True, False]).all()


def test_return_value_policy_reference():
    i1 = lg_mylib.foo_instance()
    i1.delta = 42
    i2 = lg_mylib.foo_instance()
    assert i2.delta == 42
    i2.delta = 56
    i3 = lg_mylib.foo_instance()
    assert i3.delta == 56
    print("zut")
