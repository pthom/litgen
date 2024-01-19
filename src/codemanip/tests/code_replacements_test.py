from __future__ import annotations
import os
import sys

from codemanip import code_replacements
from codemanip.code_replacements import RegexReplacementList


_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")


def test_code_replacements():
    replace_what = r"\bcv::Size\(\)"
    by_what = "(0, 0)"
    string_replacement = code_replacements.RegexReplacement(replace_what, by_what)
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = string_replacement.apply(s)
    assert r == "cv::Sizeounette cv::Size s = (0, 0)"

    replacements_str = r"""
    \bcv::Size\(\) -> (0, 0)
    """
    replacements_list = RegexReplacementList.from_string(replacements_str)
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = replacements_list.first_replacement().apply(s)
    assert r == "cv::Sizeounette cv::Size s = (0, 0)"

    replacements_str = r"""
    \bcv::Size\b -> Size
    """
    replacements_list = RegexReplacementList.from_string(replacements_str)
    s = "cv::Sizeounette cv::Size s = cv::Size()"
    r = replacements_list.first_replacement().apply(s)
    assert r == "cv::Sizeounette Size s = Size()"
