import os
import sys

this_dir = os.path.dirname(__file__)
sys.path = [this_dir] + sys.path


from _lg_imgui import *

ImVec2.__repr__ = lambda self : f"{self.x}, {self.y}"
