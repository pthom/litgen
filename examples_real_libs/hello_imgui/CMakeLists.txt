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

# Add pybind11
add_subdirectory(external/pybind11)

#
# Build hello_imgui Bound C++ library
#
set(imgui_bindings_dir ${CMAKE_CURRENT_LIST_DIR}/../imgui)
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/../imgui/external/imgui)


add_subdirectory(external/glfw)

if(NOT TARGET imgui)
    add_subdirectory(${imgui_bindings_dir} imgui_bindings_build)
endif()
set(HELLOIMGUI_USE_GLFW_OPENGL3 ON CACHE BOOL "" FORCE)
set(HELLOIMGUI_BUILD_IMGUI OFF CACHE BOOL "" FORCE)
set(HELLOIMGUI_IMGUI_SOURCE_DIR ${imgui_dir} CACHE STRING "" FORCE)
set(HELLO_IMGUI_IMGUI_SHARED ON CACHE BOOL "" FORCE)
add_subdirectory(external/hello_imgui)


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

#
# Set the rpath (see https://github.com/pybind/cmake_example/issues/11)
#

# rpath for the _hello_imgui python module
set_target_properties(${python_native_module_name} PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
if(UNIX AND NOT APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "$ORIGIN/lib/")
elseif(APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "@loader_path/lib/")
endif()
set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

# rpath for hello_imgui native library
set_target_properties(hello_imgui PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
if(UNIX AND NOT APPLE)
    set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH "$ORIGIN/")
elseif(APPLE)
    set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH "@loader_path/")
endif()
set_target_properties(hello_imgui PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

#
# Export hello-imgui symbols on Windows
#
if (WIN32)
set_target_properties(hello_imgui PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

# On Windows, install DLLs in install folder root
if (WIN32)
    install(FILES $<TARGET_RUNTIME_DLLS:${python_native_module_name}> DESTINATION .)
endif()
