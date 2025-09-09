import lg_mylib


def test_custom_bindings():
    f = lg_mylib.root_custom.Foo()
    assert f.m_value == 0
    f.set_value(42)
    assert f.get_value() == 42
    assert f.m_value == 42

    assert lg_mylib.root_custom.foo_namespace_function() == 53
    # assert lg_mylib.global_function() == 64
