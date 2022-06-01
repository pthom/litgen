import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path.append("_THIS_DIR/..")
from litgen.internal.code_replacements import standard_replacements, opencv_replacements
from litgen.options import CodeStyleOptions
import litgen.options


class LitgenParseException(Exception):
    pass
