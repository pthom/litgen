import os
import shutil


LG_PROJECTS_DIR = os.path.realpath(os.path.dirname(__file__) + "/..")


def deploy_imgui_bindings_to_child_libraries():
    """
    We want to copy the following files:
    bindings/
    ├── imgui_boxed_types.h
    ├── imgui_docking_internal_types.h
    ├── lg_imgui/
    │         ├── imgui.pyi                This file need to go to bindings/hello_imgui or bindings/lg_implot
    └── pybind_imgui.cpp

    from lg_imgui to the different children libraries
    """

    files_to_copy = [
        "imgui_boxed_types.h",
        "imgui_docking_internal_types.h",
        "pybind_imgui.cpp",
    ]

    children_libraries = ["lg_hello_imgui"]
    for child_library in children_libraries:
        print(child_library)
        src_folder = f"{LG_PROJECTS_DIR}/lg_imgui/bindings"
        dst_folder = f"{LG_PROJECTS_DIR}/{child_library}/bindings"

        for file_to_copy in files_to_copy:
            src_file = f"{src_folder}/{file_to_copy}"
            dst_file = f"{dst_folder}/{file_to_copy}"
            shutil.copy(src_file, dst_file)

        # Handle "lg_imgui/imgui.pyi",
        src_file = f"{src_folder}/lg_imgui/imgui.pyi"
        if child_library == "lg_hello_imgui":
            dst_file = f"{dst_folder}/hello_imgui/imgui.pyi"
            shutil.copy(src_file, dst_file)



if __name__ == "__main__":
    deploy_imgui_bindings_to_child_libraries()
