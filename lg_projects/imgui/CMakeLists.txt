cmake_minimum_required(VERSION 3.2)
project(lg_imgui)

# Add pybind11
add_subdirectory(external/pybind11)

set(CMAKE_CXX_STANDARD 20)

#
# Set targets names
#
set(python_native_module_name _lg_imgui) # This is the native python module `_lg_imgui`,
#    it will be wrapped in a standard python module `lg_imgui` which is located in bindings/lg_imgui

#
# Build imgui Bound C++ library
#
set(imgui_dir ${CMAKE_CURRENT_LIST_DIR}/external/imgui)
file(GLOB imgui_sources ${imgui_dir}/*.h ${imgui_dir}/*.cpp  ${imgui_dir}/misc/cpp/*.cpp ${imgui_dir}/misc/cpp/*.h)
add_library(imgui SHARED ${imgui_sources} bindings/imgui_docking_internal_types.h)
target_include_directories(imgui PUBLIC ${imgui_dir} ${CMAKE_CURRENT_LIST_DIR})
target_compile_definitions(imgui PRIVATE IMGUI_USER_CONFIG="litgen_imconfig.h")
install(TARGETS imgui DESTINATION ./lib/)

#
# Build python module that uses the library
#
set(python_module_sources
    bindings/module.cpp
    bindings/pybind_imgui.cpp
    bindings/imgui_boxed_types.h
    bindings/imgui_docking_internal_types.h
    )
pybind11_add_module(${python_native_module_name} ${python_module_sources})
target_link_libraries(${python_native_module_name} PRIVATE imgui)

install(TARGETS ${python_native_module_name} DESTINATION .)

#
# Copy the python module to the project dir post build (for editable mode)
#
add_custom_command(
    TARGET ${python_native_module_name}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
    $<TARGET_FILE:${python_native_module_name}>
    ${CMAKE_CURRENT_LIST_DIR}/bindings/lg_imgui/$<TARGET_FILE_NAME:${python_native_module_name}>
)

#
# Set the rpath (see https://github.com/pybind/cmake_example/issues/11)
#
set_target_properties(${python_native_module_name} PROPERTIES BUILD_WITH_INSTALL_RPATH TRUE)
if(UNIX AND NOT APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "$ORIGIN/lib/")
elseif(APPLE)
    set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH "@loader_path/lib/")
endif()
set_target_properties(${python_native_module_name} PROPERTIES INSTALL_RPATH_USE_LINK_PATH TRUE)

# On Windows, install DLLs in install folder root
if (WIN32)
    install(FILES $<TARGET_RUNTIME_DLLS:${python_native_module_name}> DESTINATION .)
endif()
