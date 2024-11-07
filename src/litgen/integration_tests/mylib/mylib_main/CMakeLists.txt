add_library(mylib STATIC mylib.cpp mylib.h)
target_include_directories(mylib PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/../..
    ${CMAKE_CURRENT_LIST_DIR}
    )

# Under windows, auto __declspec(dllexport)
if (WIN32)
    set_target_properties(mylib PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()
