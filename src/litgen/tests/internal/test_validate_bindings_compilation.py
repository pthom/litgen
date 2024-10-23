import litgen
from litgen.internal.validate_bindings_compilation import validate_bindings_compilation


def test_validate_bindings_compilation() -> None:
    # Validates that the cpp code can be compiled into bindings and
    # that the generated Python bindings work as expected.
    # **This kind of test is slow**, do not use it extensively in CI.

    code = """
struct Foo
{
    int x = 1;
};
    """
    python_test_code = """
import validate_bindings_compilation

def test_validate_bindings_compilation() -> None:
    foo = validate_bindings_compilation.Foo()
    assert hasattr(foo, 'x')
    assert foo.x == 1
    """

    for bind_type in litgen.BindLibraryType:
        options = litgen.LitgenOptions()
        options.bind_library = bind_type

        success = validate_bindings_compilation(
            cpp_code=code,
            options=options,
            remove_build_dir_on_success=False,
            python_test_code=python_test_code,
            show_logs=True,
            python_module_name="validate_bindings_compilation",
            work_dir="/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/litgen/src/litgen/tests/internal/ppp"
            )
        assert success
