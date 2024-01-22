set(CMAKE_CXX_STANDARD 20)
add_executable(pybind_native_debug pybind_native_debug.cpp)

find_package(pybind11 CONFIG REQUIRED)
target_link_libraries(pybind_native_debug PRIVATE pybind11::embed)
