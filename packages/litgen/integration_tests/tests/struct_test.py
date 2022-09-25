import lg_mylib


def test_struct_doc():
    assert "A superb struct" in lg_mylib.MyStruct.__doc__


def test_struct_construction():
    my_struct = lg_mylib.MyStruct(factor=42, message="World")
    assert my_struct.factor == 42
    assert my_struct.message == "World"


def test_simple_struct_members():
    my_struct = lg_mylib.MyStruct()

    my_struct.factor = 42
    assert my_struct.factor == 42


def test_stl_container_members():
    my_struct = lg_mylib.MyStruct()
    assert len(my_struct.numbers) == 0

    my_struct.numbers.append(1)
    assert len(my_struct.numbers) == 0

    my_struct.append_number_from_cpp(42)
    assert my_struct.numbers == [42]


def test_fixed_size_numeric_array_members():
    foo = lg_mylib.MyStruct()

    assert (foo.values == [0, 1]).all()
    foo.values[0] = 42
    assert (foo.values == [42, 1]).all()

    assert (foo.flags == [False, True, False]).all()
    foo.flags[0] = True
    assert (foo.flags == [True, True, False]).all()

    assert not hasattr(foo, "points")


def test_struct_simple_methods():
    my_struct = lg_mylib.MyStruct()
    my_struct.set_message("aaa")
    assert my_struct.message == "aaa"


def test_struct_static_methods():
    assert lg_mylib.MyStruct.static_message() == "Hi!"


def test_struct_not_registered():
    assert "StructNotRegistered" not in dir(lg_mylib)
