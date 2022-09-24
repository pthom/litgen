import lg_mylib

# import logging


def test_basic_enum():
    assert " A super nice enum for demo purposes" in lg_mylib.BasicEnum.__doc__
    assert lg_mylib.BasicEnum.my_enum_a == 1
    assert lg_mylib.BasicEnum.my_enum_aa == 2
    assert lg_mylib.BasicEnum.my_enum_c == lg_mylib.BasicEnum.my_enum_a | lg_mylib.BasicEnum.my_enum_c


def test_class_enum_not_registered():
    assert "ClassEnumNotRegistered" not in dir(lg_mylib)


# def test_class_enum():
#     logging.warning(f"{lg_mylib.ClassEnum.on=}")
#     # assert lg_mylib.ClassEnum.off == 1
