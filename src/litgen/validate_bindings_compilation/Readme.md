The script "src/litgen/validate_bindings_compilation/validate_bindings_compilation.py" contains a sandbox where you can:
- provide C++ sample code for which to generate bindings
  - provide options for litgen
  - provide python sample code that will test the generated bindings


It is used mainly for litgen development and testing.

Edit the file `run_validate_bindings_compilation.py` to specify some C++ and Python test code, which you want to validate.


**Example content:**
In this example, we provide a simple C++ struct where a C float array should be bound as a numpy array in Python,
and a python test that will check that the bindings work as expected.

The bindings are tested for both pybind11 and nanobind.

```python
import litgen
from litgen.validate_bindings_compilation.validate_bindings_compilation import validate_bindings_compilation


def main() -> None:
    # Validates that the cpp code can be compiled into bindings and
    # that the generated Python bindings work as expected.
    # **This kind of test is slow**, do not use it extensively in CI.
    # return
    code = """
#include <vector>

std::vector<int> range(int i) {
    std::vector<int> v;
    for (int j = 0; j < i; j++) {
        v.push_back(j);
    }
    return v;
}

    """
    python_test_code = """
import validate_bindings_compilation

def test_validate_bindings_compilation() -> None:
    c = validate_bindings_compilation.range(5)
    assert c == [0, 1, 2, 3, 4]
    """

    # for bind_type in litgen.BindLibraryType:
    for bind_type in [litgen.BindLibraryType.nanobind]:
        options = litgen.LitgenOptions()
        options.fn_params_replace_buffer_by_array__regex = r".*"
        options.bind_library = bind_type
        options.fn_params_adapt_mutable_param_with_default_value__regex = r".*"

        success = validate_bindings_compilation(
            cpp_code=code,
            options=options,
            remove_build_dir_on_success=False,
            python_test_code=python_test_code,
            show_logs=True,
            python_module_name="validate_bindings_compilation",
            # work_dir="/Users/pascal/dvp/OpenSource/ImGuiWork/_Bundle/litgen/src/litgen/tests/internal/ppp",
            # enable_hack_code=True,
        )
        assert success


if __name__ == "__main__":
    main()
```
