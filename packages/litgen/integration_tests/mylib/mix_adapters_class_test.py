from __future__ import annotations
import lg_mylib
import numpy as np


# More complex tests, where we combine litgen function adapters with classes and namespace
# The main intent of these test is to verify that the generated code compiles.
# The corresponding python test file will not test all these functions
# (as they are in fact copy/pasted/adapted from other tests)


def test_template_method():
    blah = lg_mylib.some_namespace.Blah()
    x = np.array((1, 2, 3), float)
    blah.templated_mul_inside_buffer(x, 3.0)
    assert (x == np.array((3, 6, 9), float)).all()
