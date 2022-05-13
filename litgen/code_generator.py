import os
import time

from options import code_style_implot, code_style_immvision
from code_types import *
from internal import code_utils
from internal import function_parser, enum_parser, struct_parser
from internal import function_generator, enum_generator, struct_generator
from internal import find_functions_structs_enums


_THIS_DIR = os.path.dirname(__file__)
REPO_DIR = os.path.realpath(_THIS_DIR + "/../..")


def remove_pydef_cpp(dst_filename: str):
    code_utils.write_code_between_markers(
        dst_filename,
        code_marker_in(code_type),
        code_marker_out(code_type),
        "",
        True
    )


def _generate_pydef_one_type(
        header_code: str,
        code_type: CppCodeType,
        options: CodeStyleOptions) -> str:

    fn_infos_extractors = {
        CppCodeType.STRUCT:      struct_parser.parse_struct_pydef,
        CppCodeType.ENUM_CPP_98: enum_parser.parse_enum_cpp_98_pydef,
        CppCodeType.FUNCTION:    function_parser.parse_function_declaration_pydef,
    }

    fn_code_generators = {
        CppCodeType.STRUCT:      struct_generator.generate_pydef_struct_cpp_code,
        CppCodeType.ENUM_CPP_98: enum_generator.generate_pydef_enum_cpp_98,
        CppCodeType.FUNCTION:    function_generator.generate_pydef_function_cpp_code,
    }

    pydef_codes = find_functions_structs_enums.find_functions_struct_or_enums(header_code, code_type, options)

    fn_code_generator = fn_code_generators[code_type]
    fn_infos_extractor = fn_infos_extractors[code_type]

    generated_code = ""
    for pydef_code in pydef_codes:
        infos = fn_infos_extractor(pydef_code, options)
        generated_code += fn_code_generator(infos, options)

    return generated_code


def generate_pydef_cpp(
        input_cpp_header: str,
        output_cpp_module_file: str,
        options: CodeStyleOptions
        ):

    assert os.path.isfile(input_cpp_header)
    assert os.path.isfile(output_cpp_module_file)

    header_code = code_utils.read_text_file(input_cpp_header)

    generated_code = ""
    for code_type in CppCodeType:
        generated_code += _generate_pydef_one_type(header_code, code_type, options)

    marker_in =  "<autogen:pydef_cpp>"
    marker_out =  "</autogen:pydef_cpp>"

    code_utils.write_code_between_markers(
        output_cpp_module_file,
        marker_in,
        marker_out,
        generated_code,
        flag_preserve_left_spaces=True)
