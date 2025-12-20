cmake_minimum_required(VERSION 3.14)
project(taskdaemon-cpp VERSION 0.1.0)

add_library(taskdaemon INTERFACE)
target_include_directories(taskdaemon INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_features(taskdaemon INTERFACE cxx_std_17)

find_package(nlohmann_json 3.2.0 REQUIRED)
target_link_libraries(taskdaemon INTERFACE nlohmann_json::nlohmann_json)
