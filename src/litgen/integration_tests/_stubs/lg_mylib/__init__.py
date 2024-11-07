import logging
import sys
import os


def _get_binding_type() -> str | None:
    binding_type = ""
    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, "binding.cfg")

    if os.path.isfile(fname):
        with open(fname) as f:
            binding_type = f.read().strip()

    return binding_type


if "-m" in sys.argv:
    # Possibly running `python -m lg_mylib.use`.
    logging.warning("python -m lg_mylib.use was called, not setting binding type yet")
else:
    _binding_type = _get_binding_type()
    if _binding_type == "nanobind":
        logging.warning("lg_mylib: using nanobind bindings")
        from lg_mylib._lg_mylib_nanobind import *  # type: ignore # noqa
    elif _binding_type == "pybind":
        logging.warning("lg_mylib: : using pybind bindings")
        from lg_mylib._lg_mylib_pybind import *  # type: ignore # noqa
    else:
        raise RuntimeError("lg_mylib: Bad binding type!")
