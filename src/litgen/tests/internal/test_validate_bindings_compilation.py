import litgen
from litgen.internal.validate_bindings_compilation import validate_bindings_compilation


def test_validate_bindings_compilation() -> None:
    code = """
    struct Foo {
        int x = 1;
    };
    """
    bind_type = litgen.BindLibraryType.pybind11

    options = litgen.LitgenOptions()
    options.bind_library = bind_type
    generated_code = litgen.generate_code(options, code)
    success = validate_bindings_compilation(
        cpp_bound_code=code,
        bind_library_type=bind_type,
        generated_code=generated_code,
        build_dir="/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/litgen/src/litgen/tests/internal/ppp",
        remove_build_dir_on_success=False
        )

    assert success
