# TaskDaemon Handler SDKs

Native SDKs for building TaskDaemon handlers in any language.

## Installation

| Language | Install |
|----------|---------|
| Python | `pip install taskdaemon` |
| Node.js | `npm install @taskdaemon/handler` |
| Go | `go get github.com/taskdaemon/handler-go` |
| Rust | `cargo add taskdaemon-handler` |
| Java | Maven: `com.taskdaemon:handler` |
| C# | `dotnet add package TaskDaemon.Handler` |

## Quick Start

### Python

```python
from taskdaemon import handler, Task, Success

def process(task: Task) -> Success:
    return Success({"echoed": task.task_data})

handler.run(process)
```

### Node.js

```typescript
import { run, success } from '@taskdaemon/handler';

run(task => success({ echoed: task.task_data }));
```

### Go

```go
import "github.com/taskdaemon/handler-go"

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
{"task_id":"uuid","task_type":"name","task_data":{...},"attempt":1}
```

**Output:**
```json
{"status":"success","result":{...}}
```

## Documentation

- [Python SDK](python/README.md)
- [Node.js SDK](nodejs/README.md)
- [Go SDK](go/README.md)
- [Rust SDK](rust/README.md)
- [Java SDK](java/README.md)
- [C# SDK](csharp/README.md)

## License

MIT
