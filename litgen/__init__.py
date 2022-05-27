import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR] + sys.path


class LitgenParseException(Exception):
    pass


from internal.code_replacements import standard_replacements, opencv_replacements
from options import CodeStyleOptions, code_style_implot, code_style_immvision, code_style_imgui
from options import LITGEN_OPTIONS
