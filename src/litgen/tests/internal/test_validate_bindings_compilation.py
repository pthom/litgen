import litgen
from litgen.internal.validate_bindings_compilation import validate_bindings_compilation


def test_validate_bindings_compilation() -> None:
    # Validates that the cpp code can be compiled into bindings and
    # that the generated Python bindings work as expected.
    # **This kind of test is slow**, do not use it extensively in CI.

    code = """
#include <cstddef>

template<typename T> void templated_mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
{
    for (size_t i  = 0; i < buffer_size; ++i)
        buffer[i] *= (T)factor;
}
    """
    python_test_code = """
import validate_bindings_compilation
import numpy as np

def test_validate_bindings_compilation() -> None:
    x = np.array((1.0, 2.0, 3.0))
    c = validate_bindings_compilation.templated_mul_inside_buffer(x, 3.0)
    assert (x == np.array((3.0, 6.0, 9.0))).all()
    """

    # for bind_type in litgen.BindLibraryType:
    for bind_type in [litgen.BindLibraryType.nanobind]:
        options = litgen.LitgenOptions()
        options.fn_params_replace_buffer_by_array__regex = r".*"
        options.bind_library = bind_type

        success = validate_bindings_compilation(
            cpp_code=code,
            options=options,
            remove_build_dir_on_success=False,
            python_test_code=python_test_code,
            show_logs=True,
            python_module_name="validate_bindings_compilation",
            # work_dir="/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/litgen/src/litgen/tests/internal/ppp"
        )
        assert success
