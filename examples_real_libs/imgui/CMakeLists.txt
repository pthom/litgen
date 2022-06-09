set(CMAKE_CXX_STANDARD 17)

# imgui library
file(GLOB imgui_sources imgui/*.h imgui/*.cpp)
add_library(imgui ${imgui_sources})
target_include_directories(imgui PUBLIC imgui)

add_subdirectory(bindings)
