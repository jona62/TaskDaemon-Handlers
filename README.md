# TaskDaemon Handler SDKs

Native SDKs for building TaskDaemon handlers in any language.

## Installation

Python `taskdaemon==0.1.0`, Go `v0.1.2`, npm `@taskdaemon/handler` 0.1.2, crates.io `taskdaemon-handler` 0.1.2, Maven Central `io.github.jona62:handler` 0.1.2, and NuGet `TaskDaemon.Handler` 0.1.2 are published and verified. For C++, clone the release source into your handler project's build context:

```bash
git clone --branch v0.1.2 --depth 1 https://github.com/jona62/TaskDaemon-Handlers.git vendor/TaskDaemon-Handlers
```

| Language | Installation |
|----------|--------------|
| Python | `python3 -m pip install taskdaemon==0.1.0` |
| Node.js | `npm install --save-exact @taskdaemon/handler@0.1.2`; see [Node.js](nodejs/README.md) |
| Go | `go get github.com/jona62/TaskDaemon-Handlers/go@v0.1.2` |
| Rust | `taskdaemon-handler = "=0.1.2"` in Cargo.toml; see [Rust](rust/README.md) |
| Java | Add `io.github.jona62:handler:0.1.2` from Maven Central; see [Java](java/README.md) |
| C# | `dotnet add handler/handler.csproj package TaskDaemon.Handler --version 0.1.2`; see [C#](csharp/README.md) |
| C++ | Header-only: copy `vendor/TaskDaemon-Handlers/cpp/include/taskdaemon.hpp` |

The published Python 0.1.0 package exports the `run` API used by these examples. Java uses Maven coordinate `io.github.jona62:handler:0.1.2` and package imports under `com.taskdaemon`.

See [Publishing the SDKs](PUBLISHING.md) for tested artifacts, registry account setup, trusted-publisher configuration, and the release workflow. C++ also has a tested [vcpkg overlay](cpp/packaging/README.md).

## Quick Start

### Python

```python
from taskdaemon import run, Task, Success

def process(task: Task) -> Success:
    return Success({"echoed": task.task_data})

run(process)
```

### Node.js

```typescript
import { run, success } from '@taskdaemon/handler';

run(task => success({ echoed: task.task_data }));
```

### Go

```go
import "github.com/jona62/TaskDaemon-Handlers/go"

func main() {
    taskdaemon.Run(func(task taskdaemon.Task) taskdaemon.Result {
        return taskdaemon.Success(task.TaskData)
    })
}
```

## Protocol

Handlers communicate via stdin/stdout with line-delimited JSON.

**Input:**
```json
{"task_id":"uuid","task_type":"name","task_data":{"message":"hello"},"attempt":1}
```

**Output:**
```json
{"status":"success","result":{"message":"hello"}}
```

An error response uses `status: "error"`, an `error` string, and a `retryable` boolean. A retry is scheduled only when `retryable` is true and the task's retry budget remains:

```json
{"status":"error","error":"Temporary failure","retryable":true}
```

Write exactly one response line for each request and flush it immediately. SDK runners handle the response encoding and flushing. Send application logs to stderr. The daemon skips non-JSON stdout lines, but logs that resemble response JSON can be mistaken for results. Each process handles multiple tasks. `attempt` starts at `1` and increases on retries.

Execution timeouts are configured in the daemon. Omit `timeout` in a handler's configuration to inherit `DAEMON_TASK_TIMEOUT`, which defaults to 30 seconds.

## Documentation

- [Python SDK](python/README.md)
- [Node.js SDK](nodejs/README.md)
- [Go SDK](go/README.md)
- [Rust SDK](rust/README.md)
- [Java SDK](java/README.md)
- [C# SDK](csharp/README.md)
- [C++ SDK](cpp/README.md)

## SDK checks

Run these checks from the repository root with the corresponding toolchain installed:

```bash
python3 -m unittest discover -s python/tests -v
npm install --prefix nodejs
npm test --prefix nodejs
go -C go test ./...
cargo test --manifest-path rust/Cargo.toml
cargo build --manifest-path rust/Cargo.toml --example echo
mvn -f java/pom.xml test
dotnet build csharp/TaskDaemon/TaskDaemon.Handler.csproj
dotnet run --project csharp/tests/ProtocolSmoke/ProtocolSmoke.csproj
```

The Python and Node.js tests exercise a persistent stdin/stdout process, response flushing, success/error responses, retryability, and attempt values. Go tests also cover requests larger than 64 KiB and recovery after malformed request lines.

The [SDK checks workflow](.github/workflows/sdk-checks.yml) tests all seven SDKs and builds package artifacts, including installed-consumer checks. Run the separate [publishing workflow](.github/workflows/publish-packages.yml) from `main`; it checks out the requested version's immutable release tag and uploads a selected registry after its account prerequisites are configured.

## License

MIT
