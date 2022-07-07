cmake_minimum_required(VERSION 3.17)
project(litgen)


#
# Check that we have a virtual env at the repository root
#
if (IS_DIRECTORY ${CMAKE_SOURCE_DIR}/.venv/bin)
    set(PYTHON_EXECUTABLE ${CMAKE_SOURCE_DIR}/.venv/bin/python)
elseif (IS_DIRECTORY ${CMAKE_SOURCE_DIR}/.venv/Scripts)
    set(PYTHON_EXECUTABLE ${CMAKE_SOURCE_DIR}/.venv/Scripts/python)
else()
    message(WARNING "A virtual env named .venv at the repository root is recommended
        ${CMAKE_SOURCE_DIR}/venv")
endif()


add_subdirectory(example)
add_subdirectory(lg_projects)
add_subdirectory(pybind_native_debug)
