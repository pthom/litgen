from __future__ import annotations
from codemanip import code_utils

import litgen

CODE = """
Context* GetCurrentContext();
Context* GetOther();
struct Editor
{
    struct Language { int id = 0; };
    const Language* GetLanguage() const;
};
"""


def test_return_pointer_optional():
    for bind_library in (litgen.BindLibraryType.nanobind, litgen.BindLibraryType.pybind11):
        options = litgen.LitgenOptions()
        if bind_library == litgen.BindLibraryType.nanobind:
            options.use_nanobind()
        options.fn_return_pointer_optional__regex = r"^Get(CurrentContext|Language)$"
        generated_code = litgen.generate_code(options, CODE)
        assert "Optional" not in generated_code.pydef_code
        code_utils.assert_are_codes_equal(
            generated_code.stub_code,
            '''
            def get_current_context() -> Optional[Context]:
                pass
            def get_other() -> Context:
                pass
            class Editor:
                class Language:
                    id: int = 0
                    def __init__(self, id: int = 0) -> None:
                        """Auto-generated default constructor with named params"""
                        pass
                def get_language(self) -> Optional[Editor.Language]:
                    pass
                def __init__(self) -> None:
                    """Auto-generated default constructor"""
                    pass
            ''',
        )
