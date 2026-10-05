# C++ package release preparation

The SDK is a C++17 header-only library. Version `0.1.2` installs the header, MIT license, relocatable CMake configuration, and `taskdaemon::taskdaemon` target. It requires nlohmann/json 3.2.0 or later; the dependency is not bundled.

## Validate an installation

```bash
cmake -S cpp -B build/cpp -DTASKDAEMON_BUILD_TESTS=ON -DCMAKE_INSTALL_PREFIX="$PWD/install"
cmake --build build/cpp
ctest --test-dir build/cpp --output-on-failure
cmake --install build/cpp
cmake -S cpp/tests/package-consumer -B build/consumer -DCMAKE_PREFIX_PATH="$PWD/install"
cmake --build build/consumer
ctest --test-dir build/consumer --output-on-failure
cpack --config build/cpp/CPackConfig.cmake -B build/packages
```

Ensure the JSON dependency is discoverable through `CMAKE_PREFIX_PATH` or your package-manager toolchain. The protocol consumer checks a large task, a success response with the one-based attempt label, a retryable error, and malformed input.

## vcpkg publication route

The local overlay in `vcpkg/taskdaemon-handler` is usable from the SDK checkout.

The curated submission uses the name `jona62-taskdaemon-handlers` to follow vcpkg's owner-project naming rule for a new port. The local overlay retains `taskdaemon-handler`; both expose the CMake target `taskdaemon::taskdaemon`.

Version `0.1.2` is [submitted upstream](https://github.com/microsoft/vcpkg/pull/54303) with a checked source archive, baseline entry, version database entry, and passing installed consumers. Curated registry availability is pending maintainer acceptance.

To submit a curated port:

1. Publish an immutable SDK `v0.1.2` source tag after release verification.
2. Replace the overlay's local `SOURCE_PATH` with `vcpkg_from_github` using `REPO jona62/TaskDaemon-Handlers`, the release tag or exact commit, and the downloaded archive's actual SHA512. Configure from the archive's `cpp/` subdirectory.
3. Run vcpkg manifest formatting, installation, the installed consumer test, and supported-platform CI. Add the port's version database entry using the current vcpkg contributor workflow.
4. Submit the port to `microsoft/vcpkg` for maintainer review. The port is publicly available from the curated registry only after acceptance; this process is not a token-based package upload.

The source archive must include `cpp/LICENSE`, the header, CMake files, and tests. Preserve the `nlohmann-json`, `vcpkg-cmake`, and `vcpkg-cmake-config` dependencies from the local port manifest.

Official instructions: [package a library](https://learn.microsoft.com/en-us/vcpkg/get_started/get-started-packaging), [maintainer guide](https://learn.microsoft.com/en-us/vcpkg/contributing/maintainer-guide).

## ConanCenter alternative

ConanCenter also accepts reviewed recipe pull requests rather than arbitrary direct uploads. A header-only Conan 2 recipe would export the include directory and license, declare the nlohmann_json requirement, clear binary/library directories, and test a CMake consumer. Submission requires a signed contributor license agreement, an immutable source archive with checksum, a Conan 2 test package, and maintainer acceptance. No Conan recipe or registry publication is claimed by this release preparation.

Official instructions: [header-only packages](https://docs.conan.io/2/tutorial/creating_packages/other_types_of_packages/header_only_packages.html), [ConanCenter contribution requirements](https://github.com/conan-io/conan-center-index/blob/master/CONTRIBUTING.md).
