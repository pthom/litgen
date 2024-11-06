import warnings
import logging

def _get_binding_type() -> str | None:
    import os
    import sys

    if "-m" in sys.argv:
        # Possibly running `python -m lg_mylib.use`.
        return None

    binding_type = ""
    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, "binding.cfg")

    if os.path.isfile(fname):
        with open(fname) as f:
            binding_type = f.read().strip()

    return binding_type


_binding_type = _get_binding_type()
if _binding_type == "nanobind":
    logging.warning("Using nanobind bindings")
    from lg_mylib._lg_mylib_nanobind import *  # type: ignore # noqa
elif _binding_type == "pybind":
    logging.warning("Using pybind bindings")
    from lg_mylib._lg_mylib_pybind import *  # type: ignore # noqa
else:
    warnings.warn("Binding not imported.", stacklevel=1)
