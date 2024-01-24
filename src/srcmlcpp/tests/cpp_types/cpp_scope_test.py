from __future__ import annotations
from srcmlcpp.cpp_types.scope.cpp_scope import CppScope


def test_parent_scope():
    s = CppScope.from_string("A::B::C")

    assert str(s) == "A::B::C"
    s_p1 = s.parent_scope
    assert s_p1 is not None
    assert str(s_p1) == "A::B"
    s_p2 = s_p1.parent_scope
    assert s_p2 is not None
    assert str(s_p2) == "A"
    s_p3 = s_p2.parent_scope
    assert s_p3 is not None
    assert str(s_p3) == ""
    s_p4 = s_p3.parent_scope
    assert s_p4 is None


def test_can_access_scope():
    abc = CppScope.from_string("A::B::C")
    ab = abc.parent_scope
    assert ab is not None
    a = ab.parent_scope
    assert a is not None
    root = a.parent_scope
    assert root is not None

    assert abc.can_access_scope(abc)
    assert abc.can_access_scope(ab)
    assert abc.can_access_scope(a)
    assert abc.can_access_scope(root)

    assert not a.can_access_scope(abc)
    assert not ab.can_access_scope(abc)
    assert not root.can_access_scope(abc)

    abd = CppScope.from_string("A::B::D")
    assert not abd.can_access_scope(abc)


def test_scope_hierarchy():
    abc = CppScope.from_string("A::B::C")
    assert str(abc.scope_hierarchy_list) == "[A::B::C, A::B, A, ]"
