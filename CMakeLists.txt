cmake_minimum_required(VERSION 3.17)
# This CmakeLists is not useful for srcmlcpp. It is only useful for litgen, for which it generate
# the native demos libraries (see demos/litgen/)
project(litgen)

option(LITGEN_CI "Set CI mode" OFF)
mark_as_advanced(LITGEN_CI)


function(find_python_via_poetry)
    execute_process(
        COMMAND "poetry" run which python
        OUTPUT_VARIABLE poetry_python_path_stdout
        RESULT_VARIABLE poetry_python_path_result
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ECHO_OUTPUT_VARIABLE
        ECHO_ERROR_VARIABLE
        RESULT_VARIABLE result
    )
    if (NOT result EQUAL "0")
        message(STATUS "Could not find python via poetry")
    else()
        set(PYTHON_EXECUTABLE ${poetry_python_path_stdout} CACHE STRING "Path to python exe" FORCE)
        message(STATUS "Found python via poetry: PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE}")
    endif()
endfunction()

function(find_python)
    set(PYTHON_EXECUTABLE "" CACHE STRING "Path to python exe")

    if (PYTHON_EXECUTABLE MATCHES "^$")  # if empty
        find_python_via_poetry()
        if (PYTHON_EXECUTABLE MATCHES "^$")
            message(FATAL_ERROR "Python not found, please specify its path via -DPYTHON_EXECUTABLE=path/to/python(.exe)")
        endif()
    endif()
endfunction()

find_python()
include(${CMAKE_CURRENT_LIST_DIR}/cmake/find_pybind11.cmake)
find_pybind11()

option(SRCMLCPP_BUILD_DEMOS OFF)
if (SRCMLCPP_BUILD_DEMOS)
    add_subdirectory(demos)
endif()

add_subdirectory(pybind_native_debug)

add_subdirectory(packages/litgen/integration_tests)
