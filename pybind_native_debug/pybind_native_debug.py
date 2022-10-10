#!/usr/bin/env python3
import os
import sys

import demodocking  # type:ignore


# import play_implot  # type: ignore
# import play_himgui  # type: ignore


THIS_DIR = os.path.dirname(__file__)

path_lg_project = os.path.realpath(f"{THIS_DIR}/../lg_projects/")

path_lg_imgui_playground = path_lg_project + "/lg_imgui/playground"
path_lg_implot_playground = path_lg_project + "/lg_implot/playground"
path_lg_imgui_bundle_playground = path_lg_project + "/lg_imgui_bundle/playground"
sys.path.append(path_lg_imgui_playground)
sys.path.append(path_lg_implot_playground)
sys.path.append(path_lg_imgui_bundle_playground)

# print(path_lg_imgui_playground)


demodocking.main()

# import play_with_imgui  # type: ignore
# import play_himgui
