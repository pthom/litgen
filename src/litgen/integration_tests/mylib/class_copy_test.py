from __future__ import annotations

# ruff: noqa: B017
import copy
import lg_mylib
import pytest


def test_copy_implicit_ctor():
    c = lg_mylib.Copyable_ImplicitCopyCtor()
    c.a = 5
    c2 = copy.copy(c)
    assert c2.a == c.a
    c3 = copy.deepcopy(c)
    assert c3.a == c.a


def test_copy_explicit_copy_ctor():
    c = lg_mylib.Copyable_ExplicitCopyCtor()
    c.a = 5
    c2 = copy.copy(c)
    assert c2.a == c.a
    c3 = copy.deepcopy(c)
    assert c3.a == c.a


def test_copy_private_copy_ctor():
    c = lg_mylib.Copyable_ExplicitPrivateCopyCtor()
    c.a = 5
    with pytest.raises(Exception):
        copy.copy(c)
    with pytest.raises(Exception):
        copy.deepcopy(c)


def test_copy_deleted_copy_ctor():
    c = lg_mylib.Copyable_DeletedCopyCtor()
    c.a = 5
    with pytest.raises(Exception):
        copy.copy(c)
    with pytest.raises(Exception):
        copy.deepcopy(c)


def test_copy_template():
    c = lg_mylib.aaa.Copyable_Template_int(6)
    c.value = 5
    c2 = copy.copy(c)
    assert c2.value == 5
    c3 = copy.deepcopy(c)
    assert c3.value == 5
