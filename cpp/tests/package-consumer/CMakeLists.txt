cmake_minimum_required(VERSION 3.14)
project(taskdaemon_package_consumer LANGUAGES CXX)

find_package(taskdaemon 0.1.2 CONFIG REQUIRED)
add_executable(taskdaemon_consumer ../protocol.cpp)
target_link_libraries(taskdaemon_consumer PRIVATE taskdaemon::taskdaemon)
enable_testing()
add_test(NAME installed_package_protocol COMMAND taskdaemon_consumer)
