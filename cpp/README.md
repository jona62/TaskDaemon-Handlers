# TaskDaemon C++ SDK

Header-only SDK using [nlohmann/json](https://github.com/nlohmann/json).

## Installation

### Option 1: Direct Download

```bash
curl -O https://raw.githubusercontent.com/jona62/TaskDaemon-Handlers/main/cpp/include/taskdaemon.hpp
```

### Option 2: Git Submodule

```bash
git submodule add https://github.com/jona62/TaskDaemon-Handlers.git libs/taskdaemon
```

Then include: `#include "libs/taskdaemon/cpp/include/taskdaemon.hpp"`

### Option 3: CMake FetchContent

```cmake
include(FetchContent)
FetchContent_Declare(
  taskdaemon
  GIT_REPOSITORY https://github.com/jona62/TaskDaemon-Handlers.git
  GIT_TAG v0.1.2
  SOURCE_SUBDIR cpp
)
FetchContent_MakeAvailable(taskdaemon)

target_link_libraries(your_target PRIVATE taskdaemon)
```

Use the release tag once it is published, or a reviewed commit while preparing a release.

### Option 4: Installed CMake Package

With nlohmann/json's CMake package available, install the SDK into a prefix you control:

```bash
cmake -S cpp -B build/cpp -DCMAKE_INSTALL_PREFIX="$PWD/install"
cmake --install build/cpp
```

The installed package is relocatable and locates its JSON dependency for consumers:

```cmake
find_package(taskdaemon 0.1.2 CONFIG REQUIRED)
target_link_libraries(your_target PRIVATE taskdaemon::taskdaemon)
```

Set `CMAKE_PREFIX_PATH` to your installation prefix when configuring the consumer. The existing `taskdaemon` target remains available for FetchContent/add_subdirectory users.

### Option 5: Local vcpkg Overlay

The SDK includes a tested local port at `cpp/packaging/vcpkg/taskdaemon-handler`. It packages this checkout and depends on vcpkg's `nlohmann-json`:

```bash
vcpkg install taskdaemon-handler --overlay-ports="$PWD/cpp/packaging/vcpkg"
```

Configure consumers with the vcpkg toolchain and use the installed CMake target above. This overlay is not a published curated-registry port. See [package release preparation](packaging/README.md) for the upstream submission requirements.

## Dependencies

- C++17 or later
- [nlohmann/json](https://github.com/nlohmann/json) (header-only)

## Usage

```cpp
#include "taskdaemon.hpp"
#include <algorithm>
#include <cctype>

int main() {
    taskdaemon::run([](const taskdaemon::Task& task) {
        std::string msg = task.task_data.value("message", "");
        std::transform(msg.begin(), msg.end(), msg.begin(), [](unsigned char ch) {
            return static_cast<char>(std::toupper(ch));
        });
        return taskdaemon::success({{"uppercase", msg}});
    });
}
```

## Dockerfile

```dockerfile
FROM gcc:13
RUN apt-get update && apt-get install -y nlohmann-json3-dev
COPY handler.cpp /handler.cpp
COPY taskdaemon.hpp /taskdaemon.hpp
RUN g++ -std=c++17 -O2 -o /handler /handler.cpp
CMD ["/handler"]
```

## Protocol and execution

The runner reads JSON request lines from stdin and writes one flushed JSON response line per task. Keep application logs on stderr. Successful responses use `status: "success"` and `result`; failures use `status: "error"`, `error`, and optional `retryable` (default: false). Retries require `retryable: true` and remaining retry budget. A handler request uses `attempt = stored attempts + 1`, initially `1`. The daemon's stored counter increments on retry scheduling or a Failed marking and is unchanged by success. Recovery can repeat the same request attempt.

Set timeouts in the daemon's handler configuration. Omitting `timeout` inherits `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.
