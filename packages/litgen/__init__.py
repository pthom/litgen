import os
import sys

from codemanip.code_replacements import (
    opencv_replacements,
    standard_replacements,
)
from litgen.options import (
    LitgenOptions,
    code_style_imgui,
    code_style_immvision,
    code_style_implot,
)
from litgen.generate_code import generate_files, generate_pydef, generate_pyi
