# TaskDaemon C++ SDK

Header-only SDK using [nlohmann/json](https://github.com/nlohmann/json).

## Installation

Copy `include/taskdaemon.hpp` to your project, or use CMake FetchContent:

```cmake
include(FetchContent)
FetchContent_Declare(
  taskdaemon
  GIT_REPOSITORY https://github.com/jona62/TaskDaemon-Handlers.git
  GIT_TAG main
  SOURCE_SUBDIR cpp
)
FetchContent_MakeAvailable(taskdaemon)

target_link_libraries(your_target PRIVATE taskdaemon)
```

## Dependencies

- C++17 or later
- [nlohmann/json](https://github.com/nlohmann/json) (header-only)

## Usage

```cpp
#include "taskdaemon.hpp"
#include <algorithm>

int main() {
    taskdaemon::run([](const taskdaemon::Task& task) {
        std::string msg = task.task_data.value("message", "");
        std::transform(msg.begin(), msg.end(), msg.begin(), ::toupper);
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
