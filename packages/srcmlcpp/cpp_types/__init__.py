"""
Types that will represent the CppElements tree parsed by srcML in an actionable way under python.

* `CppElement` is a wrapper around a srcLML xml node (it contains an exact copy of the original code)
* `CppElementAndComment` is a documented C++ element (with its comments on previous lines and at the end of line)

All elements are stored.

All declarations are stored in a corresponding object:
    * function -> CppFunction
     * struct -> CppStruct
    * enums -> CppEnum
    * etc.

Implementations (expressions, function calls, etc.) are stored as CppUnprocessed. It is still possible to retrieve their
original code.

See doc/srcml_cpp_doc.png
"""


from srcmlcpp.cpp_types.access_types import *
from srcmlcpp.cpp_types.cpp_blocks import *
from srcmlcpp.cpp_types.cpp_class import *
from srcmlcpp.cpp_types.cpp_decl import *
from srcmlcpp.cpp_types.cpp_element import *
from srcmlcpp.cpp_types.cpp_enum import *
from srcmlcpp.cpp_types.cpp_function import *
from srcmlcpp.cpp_types.cpp_namespace import *
from srcmlcpp.cpp_types.cpp_parameter import *
from srcmlcpp.cpp_types.cpp_template import *
from srcmlcpp.cpp_types.cpp_unprocessed import *
from srcmlcpp.cpp_types.cpp_type import *
