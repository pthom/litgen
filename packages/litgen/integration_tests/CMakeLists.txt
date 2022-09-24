cmake_minimum_required(VERSION 3.17)
cmake_policy(VERSION 3.9)
project(lg_implot)

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(external/pybind11)


####################################################
# Build testrunner Bound C++ library
####################################################
add_subdirectory(mylib)                       # Will build the library mylib
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
