import litgen
from litgen.internal import cpp_to_python


def test_standard_replacements():
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = litgen.opencv_replacements().apply(s)
    assert r == "cv::Sizeounette Size s = (0, 0)"

    s = "a = 1.5f;"
    r = litgen.opencv_replacements().apply(s)
    r = litgen.standard_code_replacements().apply(s)
    assert r == "a = 1.5;"

    s = "a = -1.5d;"
    r = litgen.standard_code_replacements().apply(s)
    assert r == "a = -1.5;"


def test_imgui_replacements():
    from litgen.options_customized.litgen_options_imgui import litgen_options_imgui, ImguiOptionsType

    options = litgen_options_imgui(ImguiOptionsType.imgui_h, docking_branch=True)
    r = cpp_to_python.function_name_to_python(options, "ColorConvertRGBtoHSV")
    assert r == "color_convert_rgb_to_hsv"
    r = cpp_to_python.function_name_to_python(options, "ColorConvertHSVtoRGB")
    assert r == "color_convert_hsv_to_rgb"
