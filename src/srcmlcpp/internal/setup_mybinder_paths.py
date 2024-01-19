"""
On mybinder, we need to do the equivalent of
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/jovyan/srcml_build_docker/lib
    export PATH=/home/jovyan/srcml_build_docker/bin:$PATH
This is done only automatically on mybinder, upon importing srcmlcpp.
"""

import os


def _is_on_mybinder() -> bool:
    """Returns True if the code is running on mybinder.org, False otherwise."""
    return os.environ.get("BINDER_SERVICE_HOST") is not None


def _set_paths_for_mybinder() -> None:
    if not _is_on_mybinder():
        return

    # add the paths
    srcml_path = "/home/jovyan/srcml_build_docker/"
    srcml_path_lib = srcml_path + "lib"
    srcml_path_bin = srcml_path + "bin"

    ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
    path = os.environ.get("PATH", "")

    if srcml_path_lib not in ld_library_path:
        ld_library_path = srcml_path_lib + ":" + ld_library_path
        os.environ["LD_LIBRARY_PATH"] = ld_library_path
        # print(f"patched LD_LIBRARY_PATH to {ld_library_path}")
    if srcml_path_bin not in path:
        path = srcml_path_bin + ":" + path
        os.environ["PATH"] = path
        # print(f"patched PATH to {path}")
