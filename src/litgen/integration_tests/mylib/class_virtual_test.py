from __future__ import annotations
import lg_mylib
import pytest


def test_my_protected_method():
    m = lg_mylib.root.inner.MyVirtualClass()
    assert m.foo_virtual_protected(1) == 43


def test_virtual_pure_raises_exception():
    m = lg_mylib.root.inner.MyVirtualClass()
    with pytest.raises(RuntimeError):
        # This should throw, since we are calling a pure virtual method
        r = m.foo_virtual_public_pure()
        print(r)


class MyVirtualClassDerived(lg_mylib.root.inner.MyVirtualClass):
    def foo_virtual_public_pure(self) -> int:
        return 3

    def foo_virtual_protected(self, x: int) -> int:
        return 4 + x

    def foo_virtual_protected_const_const(self, name: str) -> str:
        return "Bye " + name


def test_override_from_python():
    """
    for reference, we are testing against this C++ function, which will call python overrides:
        MY_API std::string foo_concrete(int x, const std::string& name)
        {
            std::string r =
                  std::to_string(foo_virtual_protected(x))
                + "_" + std::to_string(foo_virtual_public_pure())
                + "_" + foo_virtual_protected_const_const(name);
            return r;
        }
    """
    m = MyVirtualClassDerived()
    r = m.foo_concrete(42, "Laeticia")
    # print(r)
    assert r == "46_3_Bye Laeticia"


def test_combining_virtual_functions_and_inheritance():
    c = lg_mylib.root.inner.MyVirtualDerivate()
    assert c.foo_virtual_public_pure() == 53
    assert c.foo_derivate() == 48
    assert c.foo_concrete(3, "Robert") == "45_53_Hello Robert"

    class MyVirtualClassDerivedAgainFromPython(lg_mylib.root.inner.MyVirtualDerivate):
        def foo_derivate(self) -> int:
            return 49

        def foo_virtual_public_pure(self) -> int:
            return 51

    cp = MyVirtualClassDerivedAgainFromPython()
    assert cp.foo_derivate() == 49
    assert cp.foo_virtual_public_pure() == 51
    assert cp.foo_concrete(3, "Robert") == "45_51_Hello Robert"
