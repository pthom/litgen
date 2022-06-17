import os
import sys

_this_dir = os.path.dirname(__file__)
sys.path = [_this_dir] + sys.path

from _cpp_litgensample import *
