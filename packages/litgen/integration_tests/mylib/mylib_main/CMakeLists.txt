add_library(mylib STATIC mylib.cpp mylib.h)
target_include_directories(mylib PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/../..
    ${CMAKE_CURRENT_LIST_DIR}
    )
target_link_libraries(mylib pybind11::pybind11)

# Under windows, auto __declspec(dllexport)
if (WIN32)
    set_target_properties(mylib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
