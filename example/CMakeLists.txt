cmake_minimum_required(VERSION 3.2)
project(litgensample)

# Add pybind11
add_subdirectory(external/pybind11)


set(CMAKE_CXX_STANDARD 20)

#
# Set targets names
#
set(cpp_lib_name example_library)                # This is the library for which we want to build bindings

set(python_native_module_name _cpp_litgensample) # This is the native python module (`_cpp_litgensample`),
                                                 #    it will be wrapped in a standard python module `litgensample,
                                                 #    which is located in bindings/litgensample

set(autgenerate_name litgensample_autogen)       # This is a custom target that runs the autogeneration of the bindings


#
# Build Bound C++ library (this is just a dummy example external library)
#
set(cpp_lib_sources example_library/litgensample.cpp example_library/litgensample.h)
add_library(${cpp_lib_name} ${cpp_lib_sources})
target_include_directories(${cpp_lib_name} PUBLIC ${CMAKE_CURRENT_LIST_DIR}/example_library)


#
# Auto-generate the C++ binding code before building the python module
#
add_custom_target(
    ${autgenerate_name}
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_litgensample.py
    DEPENDS ${CMAKE_CURRENT_LIST_DIR}/example_library/litgensample.h
    COMMENT "autogenerate python bindings"

    # We can't use BYPRODUCTS, since
    # "The Makefile Generators will remove BYPRODUCTS and other GENERATED files during make clean."
    # (cf. https://cmake.org/cmake/help/latest/command/add_custom_target.html)
)
# ${autgenerate_name} is run before building the C++ library ${cpp_lib_name}
add_dependencies(${cpp_lib_name} ${autgenerate_name})


#
# Build python module that uses the library
#
set(python_module_sources bindings/module.cpp bindings/pybind_litgensample.cpp)
pybind11_add_module(${python_native_module_name} ${python_module_sources})
target_link_libraries(${python_native_module_name} PRIVATE ${cpp_lib_name})

install(TARGETS ${python_native_module_name} DESTINATION .)

#
# Copy the python module to the project dir post build (for editable mode)
#
add_custom_command(
    TARGET ${python_native_module_name}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:${python_native_module_name}>
    ${CMAKE_CURRENT_LIST_DIR}/bindings/litgensample/$<TARGET_FILE_NAME:${python_native_module_name}>
)
