import litgen
from codemanip import code_utils


def test_comments_exclude():
    code = """
        // A super comment
        struct Foo
        {
            // An int
            int a = 0;

            void bar(); // A bar
        };
    """
    options = litgen.LitgenOptions()
    options.comments_exclude = True
    generated_code = litgen.generate_code(options, code)

    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Foo:
            a: int = 0

            def bar(self) -> None:
                pass
            def __init__(self, a: int = 0) -> None:
                """Auto-generated default constructor with named params"""
                pass
    ''',
    )
