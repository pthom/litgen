#!/usr/bin/env python3
import sys
import os

THIS_DIR = os.path.dirname(__file__)
path_examples = os.path.realpath(f"{THIS_DIR}/../pybind_examples/")
sys.path.append(path_examples)
