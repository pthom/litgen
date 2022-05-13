set(cpp_lib_name litgensample_library)
set(python_module_name litgensample)
set(autgenerate_name litgensample_autogen)


#
# Build C++ library
#
set(cpp_lib_sources litgensample.cpp litgensample.h)
add_library(${cpp_lib_name} ${cpp_lib_sources})
target_include_directories(${cpp_lib_name} PUBLIC ${CMAKE_CURRENT_LIST_DIR})


#
# Auto-generate the C++ binding code before building the python module
#
add_custom_target(
    ${autgenerate_name}
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_litgensample.py
    DEPENDS ${CMAKE_CURRENT_LIST_DIR}/litgensample.h
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
set(python_module_sources generated_pybind/module.cpp generated_pybind/pybind_litgensample.cpp)
pybind11_add_module(${python_module_name} ${python_module_sources})
target_link_libraries(${python_module_name} PRIVATE ${cpp_lib_name})


#
# Copy the python module to the project dir post build (for editable mode)
#
add_custom_command(
    TARGET ${python_module_name}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:${python_module_name}>
    ${PROJECT_SOURCE_DIR}/$<TARGET_FILE_NAME:${python_module_name}>
)
