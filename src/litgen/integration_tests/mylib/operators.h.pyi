# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: operators.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore

from typing import overload

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:operators.h>    ####################

class IntWrapper:
    value: int
    def __init__(self, v: int) -> None:
        pass
    # arithmetic operators
    def __add__(self, b: IntWrapper) -> IntWrapper:
        pass
    @overload
    def __sub__(self, b: IntWrapper) -> IntWrapper:
        pass
    @overload
    def __neg__(self) -> IntWrapper:
        """Unary minus operator"""
        pass
    def __lt__(self, b: IntWrapper) -> bool:
        """Comparison operator"""
        pass
    # Two overload of the += operator
    @overload
    def __iadd__(self, b: IntWrapper) -> IntWrapper:
        pass
    @overload
    def __iadd__(self, b: int) -> IntWrapper:
        pass
    # Two overload of the call operator, with different results
    @overload
    def __call__(self, b: IntWrapper) -> int:
        pass
    @overload
    def __call__(self, b: int) -> int:
        pass

class IntWrapperSpaceship:
    value: int

    def __init__(self, v: int) -> None:
        pass
    # Test spaceship operator, which will be split into 5 operators in Python!
    # ( <, <=, ==, >=, >)
    # Since we have two overloads, 10 python methods will be built
    @overload
    def __lt__(self, o: IntWrapperSpaceship) -> bool:
        pass
    @overload
    def __le__(self, o: IntWrapperSpaceship) -> bool:
        pass
    @overload
    def __eq__(self, o: IntWrapperSpaceship) -> bool:
        pass
    @overload
    def __ge__(self, o: IntWrapperSpaceship) -> bool:
        pass
    @overload
    def __gt__(self, o: IntWrapperSpaceship) -> bool:
        pass
    @overload
    def __lt__(self, o: int) -> bool:
        pass
    @overload
    def __le__(self, o: int) -> bool:
        pass
    @overload
    def __eq__(self, o: int) -> bool:
        pass
    @overload
    def __ge__(self, o: int) -> bool:
        pass
    @overload
    def __gt__(self, o: int) -> bool:
        pass

####################    </generated_from:operators.h>    ####################

# </litgen_stub> // Autogenerated code end!
