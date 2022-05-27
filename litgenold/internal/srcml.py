"""
Interface to srcML (https://www.srcml.org/)
"""

import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
import time
import traceback, inspect
from dataclasses import dataclass
from typing import Callable


from srcml_types import *
from srcml_types import _str_none_empty



###########################################
#
# Parsing
#
###########################################













