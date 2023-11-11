cmake_minimum_required(VERSION 3.17)
cmake_policy(VERSION 3.9)
project(lg_implot)

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)


####################################################
# Add pybind11
####################################################
# Note there are several ways to provide pybind:
# - Method 1 (easiest): `pip install pybind11` and specify PYTHON_EXECUTABLE
# - Method 2: via a submodule +  add_subdirectory(external/pybind11)
# - Method 3: via a global install (`brew install pybind11`, `apt-get install python-pybind11`)
#      Note that apt packages may be out of date and might break the build (we require pybind11 from late 2021)
if(DEFINED PYTHON_EXECUTABLE)
    # if PYTHON_EXECUTABLE is defined, and pybind11 is installed via pip,
    # then add its path to CMAKE_PREFIX_PATH
    #
    # this is the case
    # * when using SKBUILD, which set PYTHON_EXECUTABLE
    #   (and pybind11 is referenced in pyproject.toml, section [build-system]/requires)
    # * when building normally, if you set PYTHON_EXECUTABLE
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" -c
        "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE _tmp_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
    list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")
endif()

find_package(pybind11 CONFIG REQUIRED)


####################################################
# Build testrunner Bound C++ library
####################################################
add_subdirectory(mylib/mylib_main)            # Will build the library mylib
set(bound_library mylib)                      # The library for which we are building bindings


####################################################
# Regenerate bindings before building
####################################################
if (NOT SKBUILD) # Do not run autogenerate when running pip install
    set(run_autogenerate ON)
endif()
if (run_autogenerate)
    add_custom_target(
        autogenerate_mylib ALL
        COMMAND
        ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_mylib.py
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    )
    add_dependencies(mylib autogenerate_mylib)    # Make sure autogenerate is run before building the lib
endif()


#########################################################################
# Build python module that provides bindings to the library implot
#########################################################################
set(python_native_module_name _lg_mylib) # This is the native python module name
set(python_wrapper_module_name lg_mylib) # This is the python wrapper around the native module
set(python_module_sources bindings/module.cpp bindings/pybind_mylib.cpp) # native python module sources

pybind11_add_module(${python_native_module_name} ${python_module_sources})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)
