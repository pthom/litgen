import litgen
from litgen.internal.validate_bindings_compilation import validate_bindings_compilation


def test_validate_bindings_compilation() -> None:
    # Validates that the cpp code can be compiled into bindings and
    # that the generated Python bindings work as expected.
    # **This kind of test is slow**, do not use it extensively in CI.
    # return
    code = """
#include <vector>
#include <map>
#include <string>

struct FooBrace {
    std::vector<int> int_values = {1, 2, 3};
    std::map<std::string, int> dict_string_int{{"abc", 3}};
};
    """
    python_test_code = """
import validate_bindings_compilation

def test_validate_bindings_compilation() -> None:
    c = validate_bindings_compilation.FooBrace()
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
