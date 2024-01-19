import litgen
from codemanip import code_utils


def test_export_defines():
    cpp_code = """
        #define MYLIB_VALUE 1
        #define MYLIB_FLOAT 1.5
        #define MYLIB_STRING "abc"
        #define MYLIB_HEX_VALUE 0x00010009
    """

    options = litgen.LitgenOptions()
    options.macro_define_include_by_name__regex = "^MYLIB_"
    options.macro_name_replacements.add_first_replacement(r"^MYLIB_([A-Z_]*)", r"\1")  # Suppress the "MYLIB_" prefix
    generated_code = litgen.generate_code(options, cpp_code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        VALUE = 1
        FLOAT = 1.5
        STRING = "abc"
        HEX_VALUE = 0x00010009
    """,
    )
