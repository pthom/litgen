cmake_minimum_required(VERSION 3.17)
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
    )
    if (NOT EXISTS ${poetry_python_path_stdout})
        message(FATAL_ERROR "Could not find python via poetry")
    endif()
    set(PYTHON_EXECUTABLE ${poetry_python_path_stdout} PARENT_SCOPE)
endfunction()

if(NOT DEFINED PYTHON_EXECUTABLE)
    find_python_via_poetry()
    message("Searched python via poetry: PYTHON_EXECUTABLE=${PYTHON_EXECUTABLE}")
endif()

add_subdirectory(demos)
add_subdirectory(pybind_native_debug)

add_subdirectory(packages/litgen/integration_tests)
