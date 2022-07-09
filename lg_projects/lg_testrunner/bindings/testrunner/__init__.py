import os
import sys

this_dir = os.path.dirname(__file__)
sys.path = [this_dir] + sys.path

from _testrunner import *
