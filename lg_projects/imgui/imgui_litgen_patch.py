"""
Applies a simple patch to imgui.h
This is not used anymore, since imgui binding generation now works without any modification.
"""
import os
import patch
import logging


this_dir = os.path.realpath(os.path.dirname(__file__))
imgui_dir = f"{this_dir}/imgui"

patch_file = f"{this_dir}/imgui_litgen_patch.patch"
imgui_patch = patch.fromfile(patch_file)


def apply_imgui_patch():
    patch_success = imgui_patch.apply(root=imgui_dir)
    if not patch_success:
        logging.warning("apply_imgui_patch failed")


def revert_imgui_patch():
    patch_success = imgui_patch.revert(root=imgui_dir)
    if not patch_success:
        logging.warning("revert_imgui_patch failed")


if __name__ == "__main__":
    apply_imgui_patch()
