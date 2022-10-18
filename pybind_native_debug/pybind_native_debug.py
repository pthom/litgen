#!/usr/bin/env python3
import os
import sys

THIS_DIR = os.path.dirname(__file__)


def demo_node_editor() -> None:
    path_lg_imgui_bundle = os.path.realpath(f"{THIS_DIR}/../demos/litgen/imgui_bundle/demos/")
    print(path_lg_imgui_bundle)
    sys.path.append(path_lg_imgui_bundle)
    import demo_node_editor  # type: ignore

    demo_node_editor.main()


demo_node_editor()
