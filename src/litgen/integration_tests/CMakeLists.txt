cmake_minimum_required(VERSION 3.17)
project(litgen)
set(CMAKE_CXX_STANDARD 20)


option(LITGEN_USE_NANOBIND OFF)
if (DEFINED ENV{LITGEN_USE_NANOBIND})
    set(LITGEN_USE_NANOBIND $ENV{LITGEN_USE_NANOBIND})
else()
    set(LITGEN_USE_NANOBIND OFF)
endif()
message(STATUS "LITGEN_USE_NANOBIND: ${LITGEN_USE_NANOBIND}")


if (NOT LITGEN_USE_NANOBIND)
    # pybind11 supports bindings for multiple inheritance, nanobind does not
    add_compile_definitions(BINDING_MULTIPLE_INHERITANCE)
endif()

# used by bool bindings_with_nanobind() / bool bindings_with_pybind()
if (NOT LITGEN_USE_NANOBIND)
    add_compile_definitions(BINDINGS_WITH_PYBIND)
else()
    add_compile_definitions(BINDINGS_WITH_NANOBIND)
endif()

####################################################
# Build testrunner Bound C++ library
####################################################
add_subdirectory(mylib/mylib_main)            # Will build the library mylib
set(bound_library mylib)                      # The library for which we are building bindings


####################################################
# Find pybind11 or nanobind (and find Python)
####################################################
include(litgen_cmake/litgen_cmake.cmake)
if (LITGEN_USE_NANOBIND)
    litgen_find_nanobind()
else()
    litgen_find_pybind11()
endif()


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
        ${Python_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_mylib.py no_generate_file_by_file
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    )
    add_dependencies(mylib autogenerate_mylib)    # Make sure autogenerate is run before building the lib
endif()


#########################################################################
# Build python module that provides bindings to the library implot
#########################################################################
set(python_wrapper_module_name lg_mylib) # This is the python wrapper around the native module

if (LITGEN_USE_NANOBIND)
    set(python_native_module_name _lg_mylib_nanobind) # native python module name
    set(python_module_sources _pydef_nanobind/module.cpp _pydef_nanobind/nanobind_mylib.cpp) # native python module sources
    nanobind_add_module(${python_native_module_name} ${python_module_sources})
else()
    set(python_native_module_name _lg_mylib_pybind) # native python module name
    set(python_module_sources _pydef_pybind11/module.cpp _pydef_pybind11/pybind_mylib.cpp) # native python module sources
    pybind11_add_module(${python_native_module_name} ${python_module_sources})
endif()

litgen_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
    ${CMAKE_CURRENT_LIST_DIR}/_stubs
)
