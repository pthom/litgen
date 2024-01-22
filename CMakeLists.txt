cmake_minimum_required(VERSION 3.17)
# This CmakeLists is not useful for srcmlcpp. It is only useful for litgen, for which it generate
# the native demos libraries (see demos/litgen/)
project(litgen)

option(LITGEN_CI "Set CI mode" OFF)
mark_as_advanced(LITGEN_CI)


if(NOT DEFINED PYTHON_EXECUTABLE)
    message(FATAL_ERROR "PYTHON_EXECUTABLE must be defined")
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmake/find_pybind11.cmake)
find_pybind11()

option(SRCMLCPP_BUILD_DEMOS OFF)
if (SRCMLCPP_BUILD_DEMOS)
    add_subdirectory(demos)
endif()

if (PROJECT_IS_TOP_LEVEL)
    add_subdirectory(pybind_native_debug)
endif()

add_subdirectory(src/litgen/integration_tests)
