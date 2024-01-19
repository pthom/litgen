from __future__ import annotations
import os
import sys

from litgen.internal.context.litgen_context import LitgenContext

__all__ = ["LitgenContext"]

_THIS_DIR = os.path.dirname(__file__)
sys.path.append(_THIS_DIR + "/../..")  # noqa
