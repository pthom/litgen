"""
Applies a simple patch to imgui.h that will include the std::string signatures for InputText
(taken from existing imgui/misc/cpp/imgui_stdlib.h)
"""
import os
import patch
import logging


def apply_imgui_string_patch():
    this_dir = os.path.realpath(os.path.dirname(__file__))
    imgui_dir = f"{this_dir}/imgui"

    patch_file = f"{this_dir}/imgui_string_patch.patch"
    imgui_patch = patch.fromfile(patch_file)

    patch_success = imgui_patch.apply(root=imgui_dir)
    if not patch_success:
        logging.warning("apply_imgui_string_patch failed")


if __name__ == "__main__":
    apply_imgui_string_patch()
