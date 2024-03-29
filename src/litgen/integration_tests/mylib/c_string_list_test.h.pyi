# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: c_string_list_test.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore
from typing import List

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:BoxedTypes>    ####################
class BoxedInt:
    value: int
    def __init__(self, v: int = 0) -> None:
        pass
    def __repr__(self) -> str:
        pass

####################    </generated_from:BoxedTypes>    ####################

####################    <generated_from:c_string_list_test.h>    ####################

def c_string_list_total_size(
    items: List[str], output_0: BoxedInt, output_1: BoxedInt
) -> int:
    """
    C String lists tests:
      Two consecutive params (const char *, int | size_t) are exported as List[str]

    The following function will be exported with the following python signature:
    -->    def c_string_list_total_size(items: List[str], output_0: BoxedInt, output_1: BoxedInt) -> int:

    """
    pass

####################    </generated_from:c_string_list_test.h>    ####################

# </litgen_stub> // Autogenerated code end!
