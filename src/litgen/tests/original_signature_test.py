from __future__ import annotations
import litgen
from codemanip import code_utils


def test_original_signature_not_for_synthesized_constructor():
    """The original C++ signature comment is for the header's declarations: the constructor with named params, which
    litgen invents for a struct with public members, has none"""
    options = litgen.LitgenOptions()
    options.original_signature_flag_show = True
    code = """
        struct Point {
            int x = 0;
            int y = 0;
            int norm();
        };
        """
    generated_code = litgen.generate_code(options, code)
    code_utils.assert_are_codes_equal(
        generated_code.stub_code,
        '''
        class Point:
            # int x = 0;    /* original C++ signature */
            x: int = 0
            # int y = 0;    /* original C++ signature */
            y: int = 0
            # int norm();    /* original C++ signature */
            def norm(self) -> int:
                pass
            def __init__(self, x: int = 0, y: int = 0) -> None:
                """Auto-generated default constructor with named params"""
                pass
        ''',
    )
