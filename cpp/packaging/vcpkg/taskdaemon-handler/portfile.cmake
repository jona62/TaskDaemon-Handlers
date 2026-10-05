# This overlay packages the SDK checkout containing this port.
# A curated-registry submission must download an immutable release instead.
get_filename_component(SOURCE_PATH "${CURRENT_PORT_DIR}/../../.." ABSOLUTE)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS -DTASKDAEMON_BUILD_TESTS=OFF
)
vcpkg_cmake_install()
vcpkg_cmake_config_fixup(PACKAGE_NAME taskdaemon CONFIG_PATH lib/cmake/taskdaemon)
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug" "${CURRENT_PACKAGES_DIR}/lib")
file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")
vcpkg_install_copyright(FILE_LIST "${SOURCE_PATH}/LICENSE")
