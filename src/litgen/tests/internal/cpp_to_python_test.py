from __future__ import annotations
import litgen
from litgen.internal import cpp_to_python


def test_standard_replacements():
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = litgen.opencv_replacements().apply(s)
    assert r == "cv::Sizeounette Size s = (0, 0)"

    s = "a = 1.5f;"
    r = litgen.opencv_replacements().apply(s)
    r = litgen.standard_value_replacements().apply(s)
    assert r == "a = 1.5;"

    s = "a = -1.5d;"
    r = litgen.standard_value_replacements().apply(s)
    assert r == "a = -1.5;"


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
    assert my_type_to_python("std::function<void(std::vector<int>&, const std::string&)>") == "Callable[[List[int], str], None]"
    assert my_type_to_python("std::optional<int, std::allocator<int>>") == "Optional[int, std.allocator[int]]"
    assert my_type_to_python("const std::optional<const MyVector<Inner>> &") == "Optional[MyVector[Inner]]"
    assert my_type_to_python("const std::optional<const std::vector<Inner>> &") == "Optional[List[Inner]]"

    assert my_type_to_python("std::function<void(int)>") == "Callable[[int], None]"
    assert my_type_to_python("std::function<int(std::string, double)>") == "Callable[[str, float], int]"
    assert my_type_to_python(
        "std::function<void(std::vector<int>&, const std::string&)>") == "Callable[[List[int], str], None]"

    assert my_type_to_python("std::vector<std::map<int, std::vector<std::string>>>") == "List[Dict[int, List[str]]]"
    assert my_type_to_python("std::tuple<int, std::vector<std::string>, std::map<int, float>>") == "Tuple[int, List[str], Dict[int, float]]"
    assert my_type_to_python("std::function<std::optional<std::string>(int, float)>") == "Callable[[int, float], Optional[str]]"

    assert my_type_to_python("void *") == "Any"

    # Known limitations
    # =================
    # volatile is not handled
    assert my_type_to_python("volatile int") == "volatile int"
    # unsigned char is not handled (up the user to defined another synonym)
    assert my_type_to_python("unsigned char") == "unsigned char"
