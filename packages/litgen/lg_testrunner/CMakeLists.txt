cmake_minimum_required(VERSION 3.17)
cmake_policy(VERSION 3.9)
project(lg_implot)

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(external/pybind11)

####################################################
# Build testrunner Bound C++ library
####################################################
add_subdirectory(testrunner_cpp_bound_lib)    # Will build the library testrunner
set(bound_library testrunner)                 # The library for which we are building bindings


#########################################################################
# Build python module that provides bindings to the library implot
#########################################################################
set(python_native_module_name _testrunner) # This is the native python module name
set(python_wrapper_module_name testrunner) # This is the python wrapper around the native module
set(python_module_sources bindings/module.cpp bindings/pybind_${bound_library}.cpp) # native python module sources

pybind11_add_module(${python_native_module_name} ${python_module_sources})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)
