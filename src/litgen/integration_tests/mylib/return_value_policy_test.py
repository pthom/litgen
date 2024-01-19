from __future__ import annotations
import lg_mylib


def modify_instance(value: int):
    instance = lg_mylib.MyConfig.instance()
    instance.value = value


def test_return_value_policy():
    instance = lg_mylib.MyConfig.instance()
    instance.value = 3
    assert lg_mylib.MyConfig.instance().value == 3

    modify_instance(10)
    assert instance.value == 10

    lg_mylib.my_config_instance().value = 15
    assert instance.value == 15
