import os

import litgen.internal.module_pydef_generator
from litgen import CodeStyleOptions
from litgen.internal import code_utils
import srcmlcpp


def _generate_pydef(
        code: str,
        options: CodeStyleOptions
    ) -> str:

    cpp_unit = srcmlcpp.code_to_cpp_unit(options.srcml_options, code)
    generated_code = litgen.internal.module_pydef_generator.generate_pydef(cpp_unit, options)
    return generated_code


def _run_generate(
        input_cpp_header: str,
        output_file: str,
        fn_code_generator,
        marker_token: str,
        options: CodeStyleOptions
):
    assert os.path.isfile(input_cpp_header)
    assert os.path.isfile(output_file)

    options.assert_buffer_types_are_ok()

    header_code = code_utils.read_text_file(input_cpp_header)

    generated_code = fn_code_generator(header_code, options)

    marker_in = f"<autogen:{marker_token}>"
    marker_out = f"</autogen:{marker_token}>"

    code_utils.write_code_between_markers(
        output_file,
        marker_in,
        marker_out,
        generated_code)


def generate(
        input_cpp_header: str,
        output_cpp_module_file: str,
        options: CodeStyleOptions,
        output_stub_pyi_file: str = ""
    ):

    _run_generate(input_cpp_header,
                  output_cpp_module_file,
                  _generate_pydef,
                  "pydef_cpp",
                  options)

    # if len(output_stub_pyi_file) > 0:
    #     _run_generate(input_cpp_header,
    #                   output_stub_pyi_file,
    #                   _fn_code_generator_stub,
    #                   "stub",
    #                   options)

