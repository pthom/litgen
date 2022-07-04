cmake_minimum_required(VERSION 3.2)
project(lg_imgui)

# Options: do we run the generation of the binding code, or do we use it as it is?
# It is off, because we run autogenerate_imgui.py manually (since it take about 30 seconds)
set(imgui_run_generate OFF)


# Add pybind11
add_subdirectory(pybind11)

set(CMAKE_CXX_STANDARD 20)

#
# Set targets names
#
set(cpp_lib_name imgui)                # This is the library for which we want to build bindings

set(python_native_module_name _lg_imgui) # This is the native python module (`_lg_imgui`),
#    it will be wrapped in a standard python module `lg_imgui,
#    which is located in bindings/lg_imgui

set(autgenerate_name lg_imgui_autogen)       # This is a custom target that runs the autogeneration of the bindings


#
# Build imgui Bound C++ library
#
file(GLOB cpp_lib_sources imgui/*.h imgui/*.cpp  imgui/misc/cpp/*.cpp imgui/misc/cpp/*.h)
add_library(${cpp_lib_name} SHARED ${cpp_lib_sources} bindings/imgui_docking_internal_types.h) # Hack lgimgui: shared
target_include_directories(${cpp_lib_name} PUBLIC ${CMAKE_CURRENT_LIST_DIR}/imgui)


if (imgui_run_generate)
    #
    # Auto-generate the C++ binding code before building the python module
    #
    add_custom_target(
        ${autgenerate_name}
        COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_LIST_DIR}/autogenerate_imgui.py
        DEPENDS ${CMAKE_CURRENT_LIST_DIR}/imgui/imgui.h
        COMMENT "autogenerate imgui python bindings"

        # We can't use BYPRODUCTS, since
        # "The Makefile Generators will remove BYPRODUCTS and other GENERATED files during make clean."
        # (cf. https://cmake.org/cmake/help/latest/command/add_custom_target.html)
    )
    # ${autgenerate_name} is run before building the C++ library ${cpp_lib_name}
    add_dependencies(${cpp_lib_name} ${autgenerate_name})
endif()

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
    ${CMAKE_CURRENT_LIST_DIR}/bindings/lg_imgui/$<TARGET_FILE_NAME:${python_native_module_name}>
)
