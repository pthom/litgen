import lg_mylib


def test_basic_enum():
    assert "BasicEnum: a simple C-style enum" in lg_mylib.BasicEnum.__doc__
    assert lg_mylib.BasicEnum.a == 1
    assert lg_mylib.BasicEnum.aa == 2
    assert lg_mylib.BasicEnum.c == lg_mylib.BasicEnum.a | lg_mylib.BasicEnum.c


def test_class_enum_not_registered():
    assert "ClassEnumNotRegistered" not in dir(lg_mylib)


def test_class_enum():
    assert lg_mylib.ClassEnum.on.value == 0
    assert lg_mylib.ClassEnum.off.value == 1
    assert lg_mylib.ClassEnum.unknown.value == 2
