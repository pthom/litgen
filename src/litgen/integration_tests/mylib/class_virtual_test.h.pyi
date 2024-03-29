# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: class_virtual_test.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore
# ruff: noqa: F821, B008

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:class_virtual_test.h>    ####################

#
# This test will exercise the following options:
#
#    # class_expose_protected_methods__regex:
#    # regex giving the list of class names for which we want to expose protected methods.
#    # (by default, only public methods are exposed)
#    # If set, this will use the technique described at
#    # https://pybind11.readthedocs.io/en/stable/advanced/classes.html#binding-protected-member-functions)
#    class_expose_protected_methods__regex: str = ""
#
#    # class_expose_protected_methods__regex:
#    # regex giving the list of class names for which we want to be able to override virtual methods
#    # from python.
#    # (by default, this is not possible)
#    # If set, this will use the technique described at
#    # https://pybind11.readthedocs.io/en/stable/advanced/classes.html#overriding-virtual-functions-in-python
#    #
#    # Note: if you want to override protected functions, also fill `class_expose_protected_methods__regex`
#    class_override_virtual_methods_in_python__regex: str = ""
#

# <submodule root>
class root:  # Proxy class that introduces typings for the *submodule* root
    pass  # (This corresponds to a C++ namespace. All method are static!)

    # <submodule inner>
    class inner:  # Proxy class that introduces typings for the *submodule* inner
        pass  # (This corresponds to a C++ namespace. All method are static!)

        class MyVirtualClass:
            def foo_concrete(self, x: int, name: str) -> str:
                pass
            def foo_virtual_public_pure(self) -> int:  # overridable (pure virtual)
                pass
            def __init__(self) -> None:
                """Autogenerated default constructor"""
                pass
            # <protected_methods>
            def foo_virtual_protected(self, x: int) -> int:  # overridable
                pass
            def foo_virtual_protected_const_const(
                self, name: str
            ) -> str:  # overridable
                pass
            # </protected_methods>

        class MyVirtualDerivate(Root.Inner.MyVirtualClass):
            """Here, we test Combining virtual functions and inheritance
            See https://pybind11.readthedocs.io/en/stable/advanced/classes.html#combining-virtual-functions-and-inheritance
            """

            def __init__(self) -> None:
                pass
            def foo_virtual_public_pure(self) -> int:  # overridable
                pass
            def foo_derivate(self) -> int:  # overridable
                pass
    # </submodule inner>

# </submodule root>
####################    </generated_from:class_virtual_test.h>    ####################

# </litgen_stub> // Autogenerated code end!
