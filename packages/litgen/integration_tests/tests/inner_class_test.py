import lg_mylib


def test_inner_struct():
    p = lg_mylib.ParentStruct()
    assert p.inner_struct.value == 10
    assert p.inner_struct.add(10, 5) == 15


def test_inner_enum():
    p = lg_mylib.ParentStruct()
    assert p.inner_enum == lg_mylib.ParentStruct.InnerEnum.three
