cmake_minimum_required(VERSION 3.17)
cmake_policy(VERSION 3.9)
project(lg_implot)

include(lg_cmake_utils/lg_cmake_utils.cmake)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(external/pybind11)

####################################################
# Build testrunner Bound C++ library
####################################################
set(testrunner_dir testrunner_cpp_bound_lib)
add_library(testrunner ${testrunner_dir}/testrunner.cpp ${testrunner_dir}/testrunner.h)
target_include_directories(testrunner PUBLIC ${testrunner_dir})
# Under windows, auto __declspec(dllexport)
if (WIN32)
    set_target_properties(testrunner_lib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()


#########################################################################
# Build python module that provides bindings to the library implot
#########################################################################
set(bound_library testrunner)                 # The library for which we are building bindings
set(python_native_module_name _testrunner) # This is the native python module name
set(python_wrapper_module_name testrunner) # This is the python wrapper around the native module
set(python_module_sources bindings/module.cpp bindings/pybind_${bound_library}.cpp) # native python module sources

pybind11_add_module(${python_native_module_name} ${python_module_sources})
lg_setup_module(
    ${bound_library}
    ${python_native_module_name}
    ${python_wrapper_module_name}
)
