# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: basic_test.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================
# ruff: noqa: F811
# type: ignore
import numpy as np
from typing import overload

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:basic_test.h>    ####################

def my_sub(a: int, b: int) -> int:
    """Subtracts two numbers: this will be the function's __doc__ since my_sub does not have an end-of-line comment"""
    pass

# Title that should be published as a top comment in python stub (pyi) and thus not part of __doc__
# (the end-of-line comment will supersede this top comment)
def my_add(a: int, b: int) -> int:
    """Adds two numbers"""
    pass

# my_mul should have no user doc (but it will have a typing doc generated by pybind)
# (do not remove the next empty line, or this comment would become my_mul's doc!)

def my_mul(a: int, b: int) -> int:
    pass

# <submodule math_functions>
class math_functions:  # Proxy class that introduces typings for the *submodule* math_functions
    pass  # (This corresponds to a C++ namespace. All method are static!)
    """ Vectorizable functions example
        Numeric functions (i.e. function accepting and returning only numeric params or py::array), can be vectorized
        i.e. they will accept numpy arrays as an input.

     Auto-vectorization is enabled via the following options:
         options.fn_namespace_vectorize__regex: str = r"^MathFunctions$"
         options.fn_vectorize__regex = r".*"

    """
    @staticmethod
    @overload
    def vectorizable_sum(x: float, y: float) -> float:
        pass
    @staticmethod
    @overload
    def vectorizable_sum(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        pass

# </submodule math_functions>
####################    </generated_from:basic_test.h>    ####################

# </litgen_stub> // Autogenerated code end!
