"""
Basic code manipulation utilities, based on string processing.

Used by litgen and srcmlcpp
"""
import os, sys

_THIS_DIR = os.path.dirname(__file__)
sys.path.append("_THIS_DIR/..")

from codemanip import code_utils, code_replacements
