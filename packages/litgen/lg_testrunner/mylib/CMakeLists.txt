file(GLOB_RECURSE sources src/*.cpp)
file(GLOB_RECURSE headers include/*.h)

add_library(mylib ${sources} ${headers})
target_include_directories(mylib PUBLIC ${CMAKE_CURRENT_LIST_DIR}/include)

# Under windows, auto __declspec(dllexport)
if (WIN32)
    set_target_properties(mylib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
