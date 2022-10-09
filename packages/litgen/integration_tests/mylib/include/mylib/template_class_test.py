import lg_mylib


def test_template_class_int():
    ci = lg_mylib.MyTemplateClassInt()
    assert ci.sum() == 0
    ci = lg_mylib.MyTemplateClassInt([1, 2])
    assert ci.sum() == 3
    assert ci.sum2([3, 4]) == 10


def test_template_class_string():
    ci = lg_mylib.MyTemplateClassString()
    assert ci.sum() == ""
    ci = lg_mylib.MyTemplateClassString(["a", "b"])
    assert ci.sum() == "ab"
    assert ci.sum2(["c", "d"]) == "abcd"
