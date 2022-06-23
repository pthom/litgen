import logging

from codemanip import code_replacements
from litgen.internal import cpp_to_python
import litgen


def test_standard_replacements():
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = code_replacements.apply_code_replacements(s, litgen.opencv_replacements())
    assert r == "cv::Sizeounette Size s = (0, 0)"

    s = "a = 1.5f;"
    r = code_replacements.apply_code_replacements(s, litgen.standard_code_replacements())
    assert r == "a = 1.5;"

    s = "a = -1.5d;"
    r = code_replacements.apply_code_replacements(s, litgen.standard_code_replacements())
    assert r == "a = -1.5;"
