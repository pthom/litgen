cmake_minimum_required(VERSION 3.2)
project(lg_imgui)


set(CMAKE_CXX_STANDARD 20)

set(BUILD_SHARED_LIBS ON)

#
# Set targets names
#
set(cpp_lib_name hello_imgui)                # This is the library for which we want to build bindings

set(python_native_module_name _hello_imgui) # This is the native python module (`_lg_imgui`),
#    it will be wrapped in a standard python module `lg_imgui,
#    which is located in bindings/lg_imgui

set(autgenerate_name hello_imgui_autogen)       # This is a custom target that runs the autogeneration of the bindings

# Add pybind11
add_subdirectory(third_party/pybind11)

#
# Build hello_imgui Bound C++ library
#
set(imgui_bindings_dir ${CMAKE_CURRENT_LIST_DIR}/../imgui)
set(imgui_dir ${imgui_bindings_dir}/imgui)


add_subdirectory(third_party/glfw)

if(NOT TARGET imgui)
    add_subdirectory(${imgui_bindings_dir} imgui_bindings_build)
endif()
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)
set(HELLO_IMGUI_IMGUI_SHARED ON CACHE BOOL "" FORCE)
add_subdirectory(hello_imgui)


##
## Auto-generate the C++ binding code before building the python module
##
#add_custom_target(
#    ${autgenerate_name}
#    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_hello_imgui.py
#    DEPENDS ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui.h
#    COMMENT "autogenerate imgui python bindings"
#
#    # We can't use BYPRODUCTS, since
#    # "The Makefile Generators will remove BYPRODUCTS and other GENERATED files during make clean."
#    # (cf. https://cmake.org/cmake/help/latest/command/add_custom_target.html)
#)
## ${autgenerate_name} is run before building the C++ library ${cpp_lib_name}
#add_dependencies(${cpp_lib_name} ${autgenerate_name})


#
# Build python module that uses the library
#
set(python_module_sources bindings/module.cpp bindings/pybind_hello_imgui.cpp ../imgui/bindings/pybind_imgui.cpp)
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
    ${CMAKE_CURRENT_LIST_DIR}/bindings/hello_imgui/$<TARGET_FILE_NAME:${python_native_module_name}>
)
