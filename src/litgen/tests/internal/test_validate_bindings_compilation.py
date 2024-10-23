import litgen
from litgen.internal.validate_bindings_compilation import validate_bindings_compilation


def test_validate_bindings_compilation() -> None:
    # Validates that the cpp code can be compiled into bindings and
    # that the generated Python bindings work as expected.
    # **This kind of test is slow**, do not use it extensively in CI.

    # // The constructor params will automatically be "adapted" into std::array<uint8_t, 4>
    # Color4(const uint8_t _rgba[4])
    # {
    # for (size_t i = 0; i < 4; ++i)
    # rgba[i] = _rgba[i];
    # }

    code = """
#include <cstddef>
#include <cstdint>

struct Color4
{
    uint8_t rgba[4] = {0, 0, 0, 0};
};
    """
    python_test_code = """
import validate_bindings_compilation
import numpy as np

def test_validate_bindings_compilation() -> None:
    foo = validate_bindings_compilation.Color4()
    assert hasattr(foo, 'rgba')
    foo.rgba[1] = 1
    assert foo.rgba[1] == 1
    """

    #for bind_type in litgen.BindLibraryType:
    for bind_type in [litgen.BindLibraryType.nanobind]:
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
