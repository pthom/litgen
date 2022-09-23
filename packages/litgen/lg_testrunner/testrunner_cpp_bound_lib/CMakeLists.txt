file(GLOB_RECURSE sources src/*.cpp)
file(GLOB_RECURSE headers include/*.h)

add_library(testrunner ${sources} ${headers})
target_include_directories(testrunner PUBLIC ${CMAKE_CURRENT_LIST_DIR}/include)

# Under windows, auto __declspec(dllexport)
if (WIN32)
    set_target_properties(testrunner_lib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
