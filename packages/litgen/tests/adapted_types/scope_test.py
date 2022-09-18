import litgen
from litgen.internal.adapted_types.scope import *
from litgen.internal.adapted_types.adapted_class import AdaptedClass


def test_one():
    scope = Scope(
        [
            ScopePart(ScopeType.SUBMODULE, "Root"),
            ScopePart(ScopeType.SUBCLASS, "Parent"),
            ScopePart(ScopeType.SUBCLASS, "Child"),
        ]
    )
    name = scope.pydef_scope_name()
    assert name == "pyModuleRoot_ClassParent_ClassChild"

    scope2 = Scope()
    name2 = scope2.pydef_scope_name()
    assert name2 == "m"

    assert scope.pydef_scope_name() == "pyModuleRoot_ClassParent_ClassChild"
