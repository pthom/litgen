import litgen


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
