cmake_minimum_required(VERSION 3.17)
project(litgen)
set(CMAKE_CXX_STANDARD 20)

include(litgen_cmake/litgen_cmake.cmake)
litgen_find_pybind11()


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
    if (NOT DEFINED Python_EXECUTABLE)
        message(FATAL_ERROR "Python_EXECUTABLE not defined. litgen_find_pybind11 probably failed.")
    endif()
    add_custom_target(
        autogenerate_mylib ALL
        COMMAND
        ${Python_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_mylib.py
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
litgen_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
    ${CMAKE_CURRENT_LIST_DIR}/bindings
)
