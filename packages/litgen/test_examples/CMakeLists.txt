cmake_minimum_required(VERSION 3.1)
project(litgen_test_examples)

find_package(pybind11 CONFIG REQUIRED)

function(add_litgen_test_example_folder folder_name)
    message("---- add_litgen_test_example_folder=${folder_name}")
    add_library(${folder_name} ${folder_name}/${folder_name}.h ${folder_name}/${folder_name}.cpp)
    pybind11_add_module(pybind_${folder_name} ${folder_name}/computed/pybind_${folder_name}.cpp)
    target_link_libraries(pybind_${folder_name} PRIVATE ${folder_name})
    target_include_directories(pybind_${folder_name} PRIVATE ${folder_name})
endfunction()

add_litgen_test_example_folder("basic")
