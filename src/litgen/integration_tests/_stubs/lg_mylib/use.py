def _set_binding_type(type_name: str) -> None:
    import os
    import shutil

    dirname = os.path.dirname(__file__)
    fname = os.path.join(dirname, "binding.cfg")

    with open(fname, "w") as f:
        f.write(type_name)

    # Each backend owns its own committed stub (__init__.pybind.pyi / __init__.nano.pyi).
    # The active __init__.pyi imported by the package is a generated copy and is gitignored.
    suffix = "nano" if type_name == "nanobind" else "pybind"
    src = os.path.join(dirname, f"__init__.{suffix}.pyi")
    dst = os.path.join(dirname, "__init__.pyi")
    if os.path.isfile(src):
        shutil.copyfile(src, dst)


if __name__ == "__main__":
    import sys

    _use_nanobind = "nanobind" in sys.argv
    _set_binding_type("nanobind" if _use_nanobind else "pybind")
