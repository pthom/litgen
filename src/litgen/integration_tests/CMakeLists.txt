cmake_minimum_required(VERSION 3.17)
project(litgen)
set(CMAKE_CXX_STANDARD 20)

#option(LITGEN_USE_NANOBIND OFF)
set(LITGEN_USE_NANOBIND ON CACHE BOOL "Use nanobind for bindings" FORCE)

if (NOT LITGEN_USE_NANOBIND)
    include(litgen_cmake/litgen_cmake.cmake)
    litgen_find_pybind11()

    # pybind11 supports bindings for multiple inheritance, nanobind does not
    add_compile_definitions(BINDING_MULTIPLE_INHERITANCE)

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
    set(python_module_sources _pydef_pybind11/module.cpp _pydef_pybind11/pybind_mylib.cpp) # native python module sources

    pybind11_add_module(${python_native_module_name} ${python_module_sources})
    litgen_setup_module(
        ${bound_library}
        ${python_native_module_name}
        ${python_wrapper_module_name}
        ${CMAKE_CURRENT_LIST_DIR}/_pydef_pybind11
    )

else() # if LITGEN_USE_NANOBIND
    ####################################################
    # Build testrunner Bound C++ library
    ####################################################
    add_subdirectory(mylib/mylib_main)            # Will build the library mylib
    set(bound_library mylib)                      # The library for which we are building bindings

    # cf https://nanobind.readthedocs.io/en/latest/building.html
    if (CMAKE_VERSION VERSION_LESS 3.18)
        set(DEV_MODULE Development)
    else()
        set(DEV_MODULE Development.Module)
    endif()
    find_package(Python 3.8 COMPONENTS Interpreter ${DEV_MODULE} REQUIRED)

    # Detect the installed nanobind package and import it into CMake
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
        OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
    find_package(nanobind CONFIG REQUIRED)

    set(python_native_module_name _lg_mylib) # This is the native python module name
    set(python_wrapper_module_name lg_mylib) # This is the python wrapper around the native module
    set(python_module_sources _pydef_nanobind/module.cpp _pydef_nanobind/pybind_mylib.cpp) # native python module sources

    nanobind_add_module(${python_native_module_name} ${python_module_sources})
    target_link_libraries(${python_native_module_name} PRIVATE mylib)
endif()
