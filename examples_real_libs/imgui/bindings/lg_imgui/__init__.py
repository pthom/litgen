import os, sys

this_dir = os.path.dirname(__file__)
sys.path = [this_dir] + sys.path
from _lg_imgui import *
