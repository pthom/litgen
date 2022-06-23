import os
import sys

from codemanip import code_replacements


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_code_replacements():
    string_replacement = code_replacements.StringReplacement()
    string_replacement.replace_what = r"\bcv::Size\(\)"
    string_replacement.by_what = "(0, 0)"
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = code_replacements.apply_one_replacement(s, string_replacement)
    assert r == "cv::Sizeounette cv::Size s = (0, 0)"

    replacements_str = r"""
    \bcv::Size\(\) -> (0, 0)
    """
    replacements_list = code_replacements.parse_string_replacements(replacements_str)
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = code_replacements.apply_one_replacement(s, replacements_list[0])
    assert r == "cv::Sizeounette cv::Size s = (0, 0)"

    replacements_str = r"""
    \bcv::Size\b -> Size
    """
    replacements_list = code_replacements.parse_string_replacements(replacements_str)
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = code_replacements.apply_one_replacement(s, replacements_list[0])
    assert r == "cv::Sizeounette Size s = Size()"
