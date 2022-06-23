# import os
# import time
#
# from codemanip import code_utils
# from options import code_style_implot, code_style_immvision
# from code_types import *
# from options import LitgenOptions
# from internal import function_parser, enum_parser, struct_parser
# from internal import function_generator, enum_generator, struct_generator
# from internal import find_functions_structs_enums
# from internal import stub_generator
#
#
# _THIS_DIR = os.path.dirname(__file__)
# REPO_DIR = os.path.realpath(_THIS_DIR + "/../..")
#
#
# _fn_infos_extractors = {
#     CppCodeType.STRUCT: struct_parser.parse_struct_pydef,
#     CppCodeType.ENUM_CPP_98: enum_parser.parse_enum_cpp_98_pydef,
#     CppCodeType.FUNCTION: function_parser.parse_function_declaration_pydef,
# }
#
#
# _fn_code_generators_pydef = {
#     CppCodeType.STRUCT: struct_generator.generate_pydef_struct_cpp_code,
#     CppCodeType.ENUM_CPP_98: enum_generator.generate_pydef_enum_cpp_98,
#     CppCodeType.FUNCTION: function_generator.generate_pydef_function_cpp_code,
# }
#
#
# _fn_code_generators_stub = {
#     CppCodeType.STRUCT: stub_generator.generate_struct_stub,
#     CppCodeType.ENUM_CPP_98: lambda _, __: "",
#     CppCodeType.FUNCTION: stub_generator.generate_function_stub,
# }
#
#
# def _run_codetype_and_generator(
#     header_code: str,
#     code_type: CppCodeType,
#     fn_code_generators,
#     options: LitgenOptions,
# ) -> str:
#
#     pydef_codes = find_functions_structs_enums.find_functions_struct_or_enums(header_code, code_type, options)
#
#     fn_code_generator = fn_code_generators[code_type]
#     fn_infos_extractor = _fn_infos_extractors[code_type]
#
#     generated_code = ""
#     for pydef_code in pydef_codes:
#         infos = fn_infos_extractor(pydef_code, options)
#         generated_code += fn_code_generator(infos, options)
#
#     return generated_code
#
#
# def _run_generate(
#     input_cpp_header: str,
#     output_file: str,
#     fn_code_generators,
#     marker_token: str,
#     options: LitgenOptions,
# ):
#     assert os.path.isfile(input_cpp_header)
#     assert os.path.isfile(output_file)
#
#     options.assert_buffer_types_are_ok()
#
#     header_code = code_utils.read_text_file(input_cpp_header)
#
#     generated_code = ""
#     for code_type in CppCodeType:
#         generated_code += _run_codetype_and_generator(header_code, code_type, fn_code_generators, options)
#
#     marker_in = f"<litgen_{marker_token}>"
#     marker_out = f"</litgen_{marker_token}>"
#
#     code_utils.write_generated_code_between_markers(
#         output_file,
#         marker_in,
#         marker_out,
#         generated_code,
#         flag_preserve_left_spaces=True,
#     )
#
#
# def generate(
#     input_cpp_header: str,
#     output_cpp_module_file: str,
#     options: LitgenOptions,
#     output_stub_pyi_file: str = "",
# ):
#
#     _run_generate(
#         input_cpp_header,
#         output_cpp_module_file,
#         _fn_code_generators_pydef,
#         "pydef_cpp",
#         options,
#     )
#
#     if len(output_stub_pyi_file) > 0:
#         _run_generate(
#             input_cpp_header,
#             output_stub_pyi_file,
#             _fn_code_generators_stub,
#             "stub",
#             options,
#         )
