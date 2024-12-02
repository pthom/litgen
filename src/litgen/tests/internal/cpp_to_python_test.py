from __future__ import annotations
import litgen
from litgen.internal import cpp_to_python


def test_opencv_replacements():
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = litgen.opencv_replacements().apply(s)
    assert r == "cv::Sizeounette Size s = (0, 0)"


def test_standard_replacements():
    replacements = litgen.standard_value_replacements()

    # Basic float replacements
    assert replacements.apply("a = 1.5f;") == "a = 1.5;"
    assert replacements.apply("a = -1.5d;") == "a = -1.5;"
    assert replacements.apply("a = 2.0;") == "a = 2.0;"

    # Scientific notation
    assert replacements.apply("a = 1.5e10f;") == "a = 1.5e10;"
    assert replacements.apply("a = -1.5E-3d;") == "a = -1.5E-3;"
    assert replacements.apply("a = .5e2;") == "a = .5e2;"
    assert replacements.apply("a = -1E+2f;") == "a = -1E+2;"

    # Hexadecimal literals
    assert replacements.apply("a = 0x7000000e;") == "a = 0x7000000e;"
    assert replacements.apply("a = 0x7000000f;") == "a = 0x7000000f;"
    assert replacements.apply("a = 0XABCD;") == "a = 0XABCD;"

    # Octal literals
    assert replacements.apply("a = 0755;") == "a = 0755;"  # Classic octal
    assert replacements.apply("a = 0o755;") == "a = 0o755;"  # Modern octal

    # Binary literals
    assert replacements.apply("a = 0b1010;") == "a = 0b1010;"
    assert replacements.apply("a = 0B1010;") == "a = 0B1010;"

    # True/false replacements
    assert replacements.apply("flag = true;") == "flag = True;"
    assert replacements.apply("flag = false;") == "flag = False;"

    # nullptr/nullopt/void replacements
    assert replacements.apply("p = nullptr;") == "p = None;"
    assert replacements.apply("opt = std::nullopt;") == "opt = None;"
    assert replacements.apply("auto value = void*();") == "auto value = Any();"

    # String replacements
    assert replacements.apply("s = std::string();") == 's = "";'

    # Macros
    assert replacements.apply("min = FLT_MIN; max = FLT_MAX;") == (
        "min = sys.float_info.min; max = sys.float_info.max;"
    )

    # Large integers
    assert replacements.apply("a = 0xFFFFFFFF;") == "a = 0xFFFFFFFF;"
    assert replacements.apply("a = 12345678901234567890;") == "a = 12345678901234567890;"

    # Numbers with underscores
    assert replacements.apply("a = 1'000'000;") == "a = 1_000_000;"

    # Numbers with single quotes -> Converted to underscores
    assert replacements.apply("a = 1'000'000;") == "a = 1_000_000;"
    assert replacements.apply("a = -1'234'567;") == "a = -1_234_567;"
    assert replacements.apply("a = 1'2'3'4;") == "a = 1_2_3_4;"

    # Verify valid Python syntax is preserved
    assert replacements.apply("a = 1_000_000;") == "a = 1_000_000;"
    assert replacements.apply("a = -1_234_567;") == "a = -1_234_567;"


def test_std_array():
    s = "std::array<ImVec4, ImGuiCol_COUNT> Colors;"
    r = litgen.standard_type_replacements().apply(s)
    assert r == "List[ImVec4] Colors;"
    print(r)


def test_type_to_python() -> None:
    from litgen.internal.context.litgen_context import LitgenContext

    options = litgen.LitgenOptions()
    lg_context = LitgenContext(options)

    def my_type_to_python(s: str) -> str:
        return cpp_to_python.type_to_python(lg_context, s)

    assert my_type_to_python("unsigned int") == "int"
    assert my_type_to_python("std::vector<std::optional<int>>") == "List[Optional[int]]"
    assert my_type_to_python("std::optional<std::vector<int>>") == "Optional[List[int]]"
    assert my_type_to_python("std::map<int, std::string>") == "Dict[int, str]"
    assert my_type_to_python("std::vector<std::map<int, std::string>>") == "List[Dict[int, str]]"
    assert my_type_to_python("std::map<std::string, std::vector<int>>") == "Dict[str, List[int]]"
    assert my_type_to_python("std::tuple<int, float, std::string>") == "Tuple[int, float, str]"
    assert my_type_to_python("std::function<void(int)>") == "Callable[[int], None]"
    assert my_type_to_python("std::function<int(std::string, double)>") == "Callable[[str, float], int]"
    assert my_type_to_python("std::vector<int*>") == "List[int]"
    assert my_type_to_python("std::vector<int&>") == "List[int]"
    assert my_type_to_python("std::tuple<int, float, std::string>") == "Tuple[int, float, str]"
    assert my_type_to_python("std::variant<int, float, std::string>") == "Union[int, float, str]"
    assert my_type_to_python("std::vector<std::map<int, std::vector<std::string>>>") == "List[Dict[int, List[str]]]"
    assert (
        my_type_to_python("std::function<void(std::vector<int>&, const std::string&)>")
        == "Callable[[List[int], str], None]"
    )
    assert my_type_to_python("std::optional<int, std::allocator<int>>") == "Optional[int, std.allocator[int]]"
    assert my_type_to_python("const std::optional<const MyVector<Inner>> &") == "Optional[MyVector[Inner]]"
    assert my_type_to_python("const std::optional<const std::vector<Inner>> &") == "Optional[List[Inner]]"

    assert my_type_to_python("std::function<void(int)>") == "Callable[[int], None]"
    assert my_type_to_python("std::function<int(std::string, double)>") == "Callable[[str, float], int]"
    assert (
        my_type_to_python("std::function<void(std::vector<int>&, const std::string&)>")
        == "Callable[[List[int], str], None]"
    )

    assert my_type_to_python("std::vector<std::map<int, std::vector<std::string>>>") == "List[Dict[int, List[str]]]"
    assert (
        my_type_to_python("std::tuple<int, std::vector<std::string>, std::map<int, float>>")
        == "Tuple[int, List[str], Dict[int, float]]"
    )
    assert (
        my_type_to_python("std::function<std::optional<std::string>(int, float)>")
        == "Callable[[int, float], Optional[str]]"
    )

    assert my_type_to_python("void *") == "Any"

    # Known limitations
    # =================
    # volatile is not handled
    assert my_type_to_python("volatile int") == "volatile int"
    # unsigned char is not handled (up the user to defined another synonym)
    assert my_type_to_python("unsigned char") == "unsigned char"
