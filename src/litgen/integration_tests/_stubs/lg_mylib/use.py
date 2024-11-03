
def _set_binding_type(type_name):
    import os

    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, "binding.cfg")

    with open(fname, "w") as f:
        f.write(type_name)


if __name__ == "__main__":
    import sys
    _use_nanobind = "nanobind" in sys.argv
    _set_binding_type("nanobind" if _use_nanobind else "pybind")
