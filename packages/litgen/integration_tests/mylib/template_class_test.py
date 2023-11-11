from __future__ import annotations
import lg_mylib


def test_template_class_int():
    ci = lg_mylib.MyTemplateClass_int()
    assert ci.sum() == 0
    ci = lg_mylib.MyTemplateClass_int([1, 2])
    assert ci.sum() == 3
    assert ci.sum2([3, 4]) == 10


def test_template_class_string():
    ci = lg_mylib.MyTemplateClass_string()
    assert ci.sum() == ""
    ci = lg_mylib.MyTemplateClass_string(["a", "b"])
    assert ci.sum() == "ab"
    assert ci.sum2(["c", "d"]) == "abcd"
