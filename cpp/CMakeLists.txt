cmake_minimum_required(VERSION 3.14)
project(taskdaemon-cpp VERSION 0.1.2 LANGUAGES CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

add_library(taskdaemon INTERFACE)
add_library(taskdaemon::taskdaemon ALIAS taskdaemon)
target_include_directories(taskdaemon INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_compile_features(taskdaemon INTERFACE cxx_std_17)

find_package(nlohmann_json 3.2.0 CONFIG REQUIRED)
target_link_libraries(taskdaemon INTERFACE nlohmann_json::nlohmann_json)

install(TARGETS taskdaemon EXPORT taskdaemonTargets)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(FILES LICENSE DESTINATION ${CMAKE_INSTALL_DATADIR}/taskdaemon)
install(EXPORT taskdaemonTargets
    NAMESPACE taskdaemon::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/taskdaemon
)
configure_package_config_file(
    cmake/taskdaemonConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/taskdaemonConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/taskdaemon
)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/taskdaemonConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMinorVersion
    ARCH_INDEPENDENT
)
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/taskdaemonConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/taskdaemonConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/taskdaemon
)

option(TASKDAEMON_BUILD_TESTS "Build the SDK protocol consumer test" OFF)
if(TASKDAEMON_BUILD_TESTS)
    enable_testing()
    add_executable(taskdaemon_protocol_test tests/protocol.cpp)
    target_link_libraries(taskdaemon_protocol_test PRIVATE taskdaemon::taskdaemon)
    add_test(NAME taskdaemon_protocol COMMAND taskdaemon_protocol_test)
endif()

set(CPACK_PACKAGE_NAME taskdaemon-handler)
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "TaskDaemon header-only C++ handler SDK")
set(CPACK_PACKAGE_FILE_NAME "taskdaemon-handler-${PROJECT_VERSION}")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_GENERATOR TGZ)
include(CPack)
