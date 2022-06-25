"""
Interface to srcML (https://www.srcml.org/)
"""
from srcmlcpp.srcml_options import SrcmlOptions
from srcmlcpp.srcmlcpp_main import code_to_cpp_unit, code_to_srcml_xml_wrapper
from srcmlcpp.internal.srcml_warnings import SrcMlExceptionDetailed, emit_srcml_warning, emit_warning

# for tests
from srcmlcpp.srcmlcpp_main import code_first_enum, code_first_struct, code_first_decl, code_first_function_decl
