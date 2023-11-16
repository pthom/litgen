import litgen
from codemanip import code_utils


def test_adapted_function_api():
    options = litgen.LitgenOptions()
    options.srcmlcpp_options.functions_api_prefixes = "MY_API"
    options.fn_exclude_non_api = True

    code = """
        MY_API int foo();
        void bar();
    """
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo() -> int:
            pass
        """,
    )

    options.fn_exclude_non_api = False
    options.fn_non_api_comment = "(This API is private)"
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        def foo() -> int:
            pass
        def bar() -> None:
            """((This API is private))"""
            pass
        ''',
    )

    options.fn_non_api_comment = ""
    generated_code = litgen.generate_code(options, code)
    # print(generated_code.stub_code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        """
        def foo() -> int:
            pass
        def bar() -> None:
            pass
        """,
    )
