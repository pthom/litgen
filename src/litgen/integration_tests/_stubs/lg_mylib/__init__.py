#  type: ignore
from __future__ import annotations

def _get_binding_type():
    import os

    binding_type = ""
    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, "binding.cfg")

    if os.path.isfile(fname):
        with open(fname) as f:
            binding_type = f.read().strip()

    return binding_type


_binding_type = _get_binding_type()
if _binding_type == "nanobind":
    from lg_mylib._lg_mylib_nanobind import *  # type: ignore # noqa
if _binding_type == "pybind":
    from lg_mylib._lg_mylib_pybind import *  # type: ignore # noqa
